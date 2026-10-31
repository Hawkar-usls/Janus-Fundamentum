# -*- coding: utf-8 -*-
"""
BENCHMARK: Адаптивный тест на реальном SHA-256 (эмуляция пула NerdMinerV2).
Сложность = уровень шума в nonce (от линейного роста до случайного).
Модель учится предсказывать следующий хеш по предыдущим.
"""

import os, time, csv, random, hashlib, struct
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ==============================================================================
# Конфигурация
# ==============================================================================
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
N_SEEDS = 3                 # запуски с разными инициализациями
TRAIN_STEPS = 5000
LEARNING_RATE = 0.001

VOCAB_SIZE = 256            # предсказываем байты хеша (0..255)
BYTES_PER_HASH = 32

# Тренировочные данные: очень простой nonce (линейный рост)
TRAIN_SEQ_LEN = 64          # байт (2 хеша по 32 байта)
TRAIN_NUM_NONCES = 10       # количество разных стартовых nonce
TRAIN_NOISE_LEVEL = 0.0     # без шума = идеально предсказуемо

# Параметры адаптивного теста
MAX_NOISE_LEVEL = 1.0       # 1.0 = полностью случайный nonce
NOISE_STEP = 0.1            # шаг увеличения шума
MAX_SEQ_LEN = 512           # байт (16 хешей)
THRESHOLD_LOSS = 4.5        # ниже 5.545 – модель что-то улавливает

# Модель (маленький трансформер)
N_EMBD = 32
N_LAYER = 2
N_HEAD = 2
BLOCK_SIZE = 1024

# ==============================================================================
# Генератор данных: реальный SHA-256 с управляемой случайностью nonce
# ==============================================================================
def sha256_mining_chain(num_sequences, seq_len_bytes, num_nonces,
                        noise_level=0.0, device='cpu'):
    """
    Генерирует цепочки хешей SHA-256, как в майнинге.
    Заголовок: 4 байта (block_id) + 4 байта (nonce) + добивка нулями до 32 байт.
    nonce меняется от 0 с шагом 1, но с добавлением шума noise_level.
    При noise_level=0 nonce = фиксированный стартовый номер + шаг.
    При noise_level=1 nonce – случайное число в каждом шаге.
    """
    data = []
    for i in range(num_sequences):
        # Базовое смещение для nonce (для разнообразия)
        nonce_start = i % num_nonces
        chain = bytearray()
        # Текущий nonce (начальный)
        current_nonce = nonce_start
        # Заголовок: 32 байта, заполненные по шаблону
        while len(chain) < seq_len_bytes:
            # Собираем заголовок
            header = bytearray(32)
            # block_id = i (фиксированный для цепочки)
            header[0:4] = struct.pack('<I', i)
            # nonce с шумом
            if noise_level < 1e-6:
                use_nonce = current_nonce
            else:
                # Интерполируем между детерминированным и случайным
                if random.random() < noise_level:
                    use_nonce = random.randint(0, 2**32-1)
                else:
                    use_nonce = current_nonce
            header[4:8] = struct.pack('<I', use_nonce & 0xFFFFFFFF)
            # Остальное нули (можно добавить другие поля)
            # Вычисляем SHA-256
            hash_bytes = hashlib.sha256(bytes(header)).digest()
            chain.extend(hash_bytes)
            # Увеличиваем nonce для следующего шага (если не шум)
            current_nonce += 1
        chain = chain[:seq_len_bytes]
        data.append(torch.tensor(list(chain), dtype=torch.long, device=device))
    return data

# ==============================================================================
# Модель (тот же трансформер)
# ==============================================================================
class HashPredictor(nn.Module):
    def __init__(self, vocab_size=256, n_embd=32, n_head=2, n_layer=2, block_size=1024):
        super().__init__()
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.block_size = block_size
        self.n_head = n_head
        self.n_layer = n_layer

        self.wte = nn.Embedding(vocab_size, n_embd)
        self.wpe = nn.Embedding(block_size, n_embd)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=n_embd, nhead=n_head, dim_feedforward=4*n_embd,
            dropout=0.1, activation='relu', batch_first=True, norm_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layer)
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx):
        seq_len = idx.size(0)
        if seq_len > self.block_size:
            idx = idx[:self.block_size]
            seq_len = self.block_size
        pos = torch.arange(0, seq_len, device=idx.device)
        tok_emb = self.wte(idx)
        pos_emb = self.wpe(pos)
        x = tok_emb + pos_emb
        x = x.unsqueeze(0)
        attn_mask = torch.triu(torch.ones(seq_len, seq_len, device=idx.device) * float('-inf'), diagonal=1)
        x = self.transformer_encoder(x, mask=attn_mask)
        x = x.squeeze(0)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        return logits

# ==============================================================================
# Обучение
# ==============================================================================
def train_model(model, train_data, steps=TRAIN_STEPS, lr=LEARNING_RATE, device='cpu'):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for step in range(steps):
        seq = random.choice(train_data).to(device)
        logits = model(seq)
        shift_logits = logits[:-1, :]
        shift_labels = seq[1:]
        loss = F.cross_entropy(shift_logits, shift_labels)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % 1000 == 0 and step > 0:
            print(f"  Step {step}: loss={loss.item():.4f}")
    model.eval()
    return model

# ==============================================================================
# Адаптивный тест (увеличиваем шум nonce)
# ==============================================================================
def adaptive_test(model, device='cpu'):
    noise = 0.0
    seq_len = 64               # начинаем с двух хешей
    num_nonces = 5
    level = 0
    max_noise_reached = 0.0

    while noise <= MAX_NOISE_LEVEL + 1e-6:
        test_data = sha256_mining_chain(
            num_sequences=50,
            seq_len_bytes=seq_len,
            num_nonces=num_nonces,
            noise_level=noise,
            device=device
        )
        total_loss = 0.0
        count = 0
        with torch.no_grad():
            for seq in test_data:
                logits = model(seq)
                shift_logits = logits[:-1, :]
                shift_labels = seq[1:]
                loss = F.cross_entropy(shift_logits, shift_labels)
                total_loss += loss.item()
                count += 1
        avg_loss = total_loss / count
        print(f"  Уровень {level}: noise={noise:.1f}, len={seq_len}, nonces={num_nonces}, loss={avg_loss:.4f}")

        if avg_loss > THRESHOLD_LOSS:
            break

        max_noise_reached = noise
        level += 1
        # Увеличиваем сложность
        noise = round(noise + NOISE_STEP, 2)
        seq_len = min(MAX_SEQ_LEN, seq_len * 2)
        num_nonces = min(100, num_nonces * 2)

    return max_noise_reached, avg_loss

# ==============================================================================
# Главный эксперимент
# ==============================================================================
if __name__ == "__main__":
    print(f"Устройство: {DEVICE}")
    # Генерируем лёгкие тренировочные данные (noise=0)
    train_data = sha256_mining_chain(
        num_sequences=200,
        seq_len_bytes=TRAIN_SEQ_LEN,
        num_nonces=TRAIN_NUM_NONCES,
        noise_level=TRAIN_NOISE_LEVEL,
        device='cpu'
    )

    for seed in range(N_SEEDS):
        print(f"\n=== Запуск {seed+1}/{N_SEEDS} ===")
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

        model = HashPredictor(
            vocab_size=VOCAB_SIZE,
            n_embd=N_EMBD,
            n_head=N_HEAD,
            n_layer=N_LAYER,
            block_size=BLOCK_SIZE
        ).to(DEVICE)

        start = time.time()
        model = train_model(model, train_data, steps=TRAIN_STEPS, device=DEVICE)
        elapsed = time.time() - start

        max_noise, final_loss = adaptive_test(model, device=DEVICE)
        print(f"  Итог: модель предсказывает при шуме до {max_noise:.1f} (loss={final_loss:.4f}), время={elapsed:.1f}с")
