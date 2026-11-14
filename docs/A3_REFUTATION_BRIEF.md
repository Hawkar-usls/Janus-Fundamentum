# A3_REFUTATION_BRIEF

**Версия brief 1.0 · registration revision 1.0.1 · 14 ноября 2026 · язык проверки: точная конечная арифметика.**

Практический протокол независимой попытки опровергнуть **замороженную** A3 endpoint-compression / ternary-DP theorem. Документ фиксирует объект проверки, конечный эксперимент, критерии контрпримера, разделение статусов и порядок публикации. Он не объявляет ни доказательство A3, ни её опровержение, ни внешнюю репликацию. Полный зарегистрированный эксперимент **ещё не выполнен**. Выполнен только явно выделенный предварительный отрицательный контроль процедуры (§8).

Нормативные параметры эксперимента приведены в приложении A; исполнимый пилот и его фактический результат — в приложениях B–C. Это единый brief с приложениями; отдельный JSON содержит те же параметры для автоматической обработки.

## 1. Точный объект и происхождение утверждений

Снимки получены из актуальных публичных источников 14 ноября 2026. «Актуальный» здесь означает прочитанный снимок, закреплённый SHA, а не обещание, что ветки впоследствии не изменятся.

| Роль | Закреплённый объект |
|---|---|
| Навигация Janus-Fundamentum | `76de4c084a178fdaef7576b7128be36486072e76` |
| **Математическая цель этой проверки / publication target** | **`811d954e52296893898062d9abea7aaf572629be`** |
| Endpoint-compression proof head | `6ca16581eff08103698250b09ea51aeccd9f800b` |
| Strengthened DP proof head | `0e505f460ec63cbb358c7f66cde18ab8a52684d3` |
| Theorem evidence head | `5ee79fc82613f24e621595afa0119312a2f52660` |
| Meta Registry | `556424f457272d78a614642d8022c4e81c57929c` |

Основные первичные источники:

1. [Точное утверждение A3](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/publication/A3_TERNARY_DP/THEOREM_STATEMENT.tex), blob `be603712c7ab05021c09e0388f9cf5a8c66afe66`.
2. [Доказательство endpoint compression](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/publication/A3_TERNARY_DP/proof_endpoint_compression.tex), blob `832382cf89ffa342118fa17fe043e0b98ceb7767`.
3. [Доказательство ternary DP](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/publication/A3_TERNARY_DP/proof_ternary_dp.tex), blob `deed1217df12af0f120edf6215d7ce9ec16931ce`.
4. [Compression theorem JSON](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/research_targets/A3_KCLASS_ENDPOINT_COMPRESSION_THEOREM_V1.json), blob `84436cacf3da5e99cb79503f33ae83941950112f`; [DP theorem JSON](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/research_targets/A3_KCLASS_ENDPOINT_DP_THEOREM_V1.json), blob `a7651ac5f011a289ff1f81a0578ab2a95f965afa`.
5. [Publication manifest](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/publication/A3_TERNARY_DP/PUBLICATION_MANIFEST.json), blob `07dd7dcb88030a19d1a7b4401b7c3683592221bc`; [admission receipt v1.1](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/811d954e52296893898062d9abea7aaf572629be/research_targets/audits/A3_KCLASS_ENDPOINT_DP_V1_1_ADMISSION_0E505F46.json), blob `cfac9bba49bb4fdaed1caeca29b3e5645e900404`.
6. [Текущая навигация A3](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/76de4c084a178fdaef7576b7128be36486072e76/docs/A3_PUBLICATION_TRACK.md) и [external-review freeze, issue #173](https://github.com/Hawkar-usls/Janus-Fundamentum/issues/173). Issue — изменяемый источник; на момент чтения открыт, `updated_at=2026-08-09T00:41:01Z`, комментариев 0.
7. [Meta Registry: CURRENT-PORTFOLIO-AUTHORITY](https://github.com/Hawkar-usls/janus-meta-registry/blob/556424f457272d78a614642d8022c4e81c57929c/registry/research_portfolio/CURRENT-PORTFOLIO-AUTHORITY.json), blob `1333351624bb0beaef10ac52334ea643d29bab17`: старый portfolio master от 7 августа исторический; текущая математическая граница задаётся отдельным проектом и issue #173.
8. [Meta Registry: приглашение к проверке](https://github.com/Hawkar-usls/janus-meta-registry/blob/556424f457272d78a614642d8022c4e81c57929c/data/GAMARJOBA-GEN-ANCVALE-v1.0.json), blob `61a6c0aac53db6f9d8d3577ad27653e5453fe65a`; [правила чтения Registry](https://github.com/Hawkar-usls/janus-meta-registry/blob/556424f457272d78a614642d8022c4e81c57929c/README.md). Приглашение, регистрация и hash не равны независимой валидации.

Текущие **заявленные репозиторием** статусы: scoped theorem admitted / ES5; `EXTERNAL_INDEPENDENT_REPLICATION=NOT_ESTABLISHED`; `WORLD_NOVELTY_N4=NOT_ESTABLISHED`; `P_VS_NP=OPEN`. Сборка одного PDF на двух runner — статус воспроизводимости сборки. Этот brief не проверял повторно admission receipts, все CI-артефакты и PDF и не присваивает им новые статусы. Внутри theorem JSON сохранились исторические candidate-поля; их нельзя смешивать с более поздним admission manifest.

В исследованных источниках не найдена новая независимая репликация или A3-specific preregistration, закрывающая issue #173. Это ограниченный результат поиска, не утверждение об отсутствии таких объектов во всём интернете. Нового поиска мировой литературы в рамках brief не проведено.

## 2. Контракт задачи: только определения из A3 и явно обозначенная модель аудита

Исходная область: конечномерное пространство над конечным полем `F`; `k` **различных геометрических подпространств** `U_j`; положительные целые кратности `a_j`. Два разных базиса одного подпространства не образуют два геометрических класса. Обозначим множество индексов источника `I={1,...,k}`; это то же множество, которое в A3 обозначено `K`. Оно отличается от верхнего предела `K_max` в §5.

Layout — слово `σ` длины `n=sum(a_j)`, содержащее ровно `a_j` копий каждого индекса. На разрезе `i=0,...,n`:

```text
L_i = span всех векторов классов в σ[0:i]
R_i = span всех векторов классов в σ[i:n]
w_i = dim(L_i ∩ R_i)
W(σ) = max_i w_i
OPT(U,a) = min по всем допустимым σ W(σ)
```

Это **bottleneck min–max**, а не сумма стоимостей. Сжатие заменяет `a_j` на `b_j=min(a_j,2)`, оставляя единственную копию singleton и первую/последнюю копии repeated. Основная проверяемая цель: `OPT(U,a)=OPT(U,b)`. Более сильное утверждение источника — удаление средних копий и обратная вставка сохраняют ширину каждого соответствующего layout.

**Модель аудита**, выведенная из этого контракта, а не объявленная новым определением A3: полное состояние `c=(c_1,...,c_k)`, `0<=c_j<=a_j`, количество уже обработанных копий. Допустимый атомарный переход — `c→c+e_j` при `c_j<a_j`. Любое такое `c` достижимо из 0 и имеет продолжение до `a`; дополнительных ограничений порядка в этой A3 нет.

```text
P(c) = {j : c_j=a_j}        # finished
S(c) = {j : c_j>0}          # started
q(c) = (P(c),S(c))
rho(X) = dim(sum_{j in X} U_j)
lambda(P,S) = rho(S)+rho(I\P)-rho(I)
```

Singleton не может быть Active. У repeated есть NotStarted / Active / Done. Действительные side spans задаются `S` и `I\P`; width зависит только от `q(c)`. Предварительная беседа не является источником определения «residual»: неизвестную residual-сигнатуру мы не изобретаем и не отождествляем с `q` без указания области.

Кандидатный DP следует ровно опубликованным переходам:

```text
singleton j not in S:   (P,S) -> (P∪{j},S∪{j})
repeated j not in S:    (P,S) -> (P,S∪{j})
repeated j in S\P:      (P,S) -> (P∪{j},S)
dp[∅,∅]=0
dp[next]=min(dp[next],max(dp[current],lambda(next)))
answer=dp[I,I]
```

Вычислять числа и веса точно; значение `∞` для недостигнутого состояния не путать с нулём. Если реконструируется решение, сохранять parent и event с типом atom/start/finish. Для полного слова witness выдавать отдельные occurrence IDs или однозначное правило их назначения.

## 3. Три графа и достижимые переходы

| Объект | Вершины | Переходы / что считается |
|---|---|---|
| Полный occurrence-count graph | `prod_j(a_j+1)` | `sum_j a_j*prod_{h≠j}(a_h+1)` атомарных рёбер |
| Проекция атомарного графа через `q` | Endpoint-состояния | Включает петли при обработке средних копий; один и тот же abstract target не обязан быть доступен за один шаг из каждого представителя |
| **A3 endpoint DAG** | **`2^s*3^r`** | Только atom/start/finish, без средних копий и петель |

Здесь `s=#{j:a_j=1}`, `r=#{j:a_j>=2}`, `s+r=k`. В A3 endpoint DAG каждое допустимое состояние достижимо из `(∅,∅)` и может дойти до `(I,I)`: сначала выполнить перечисленные started/finished события в подходящем порядке, затем оставшиеся. Число его направленных рёбер:

```text
s*2^(s-1)*3^r + 2*r*2^s*3^(r-1)
```

Слагаемое отсутствующего типа равно 0; вычисление не должно обращаться к отрицательным степеням как к обязательной промежуточной целочисленной операции. Это не количество layouts, исходных occurrence-рёбер или рёбер, переживших фильтр `width<=B`. Если аудитор использует фильтр по `B`, он отдельно перечисляет достижимость и счётчики **отфильтрованного** графа и не сравнивает их с полной формулой.

У repeated с `a_j>=3` переход endpoint `finish(j)` — допустимое следующее **событие**, но из конкретного состояния с несколькими оставшимися копиями он может требовать несколько атомарных шагов. Сначала вставляются middle copies, затем last. У них сохраняется endpoint-state до последнего шага. Это место, где смешение графов порождает ложные контрпримеры.

Локальная неточность исходного DP JSON: поле `topological_measure` говорит, что `|P|+|S|` возрастает ровно на один на каждом переходе. Для singleton прирост равен двум. Строгого возрастания достаточно для DAG, а опубликованное доказательство использует именно его. Это замечание к формулировке; опровержением A3 оно не является. Алгоритмы в рамках brief не исправляются.

## 4. Что именно должны сохранять сжатие и восстановление

### 4.1 Cost-preserving strong bisimulation — достаточный, потенциально избыточный тест

Для заданного отношения `~`, сохраняющего начальные/терминальные признаки и веса, strong bisimulation требует: из `x~y` и каждого помеченного шага `x --j--> x'` существует шаг `y --j--> y'` с `x'~y'`, и наоборот. Для A3 сохранять нужно bottleneck-вес, с агрегацией пути через `max`, а не вымышленное аддитивное приращение. При корректных условиях такой тест достаточен для сохранения возможных взвешенных трасс и оптимума.

Но на **атомарном** графе отношение `q(x)=q(y)` может не быть strong bisimulation. При `a_1=3`, `x_1=1`, `y_1=2` оба класса Active; следующий атомарный шаг ведёт соответственно в Active и Done. Нарушение этого более сильного свойства записывать как `STRONG_BISIMULATION_ONLY`, пока не показано нарушение действительной цели A3. Аналогию с Markov lumpability не использовать как доказательство: здесь нет заданной вероятностной цепи.

### 4.2 Continuation equivalence — уточнять алфавит и отношение на трассах

Множества **сырых** suffix-слов из двух `c` с одним `q` могут различаться длиной и остаточными кратностями. Равенство сырых языков не является заявлением A3. Для endpoint-проверки определить нормализацию: проектировать последовательность в `q`, удалять подряд идущие повторения, отмечать class ID и тип endpoint-event. Сравнивать допустимые нормализованные продолжения с их bottleneck-стоимостью; расширять их с учётом исходных `a` и уже выполненных `c`.

Сохраняющая стоимость weak/stuttering-связь или двусторонняя trace correspondence — подходящие достаточные конструкции, если явно доказаны lifting, терминальность и max-стоимость. Не объявлять их автоматически эквивалентными strong bisimulation и не выводить их только из равенства оптимумов. Аудит продолжений проверяет **все достижимые** конкретные состояния/истории в конечном наборе, а не произвольные невалидные пары.

### 4.3 Достаточная цель для оптимальной стоимости слабее бисимуляции

Для корневого оптимума достаточно двух отображений:

1. Каждый полный layout `σ` переводится в legal endpoint-layout `C(σ)` с `W(C(σ))<=W(σ)`.
2. Каждый legal endpoint-layout `τ` имеет full lift `E_a(τ)` с `W(E_a(τ))<=W(τ)`.

Отсюда `OPT_endpoint<=OPT_full` и `OPT_full<=OPT_endpoint`. Источник заявляет более сильное pathwise равенство ширин при удалении/вставке middle copies; именно его также атакует эксперимент. Несовпадение неопределённых «добавочных стоимостей» ещё не является refutation. Равенство `V*(x)=V*(y)` для некоторых состояний, в свою очередь, не доказывает ни trace correspondence, ни корректность корневого DP.

Для локальной диагностики можно определить `V*(c)=min_suffix max(width(c), все будущие width)` с явной терминальной конвенцией. Различие `V*` у представителей опровергает соответствующую **локально заявленную** value-equivalence, если она имеется; оно не автоматически опровергает любой корневой compression theorem. Нужно назвать нарушенный пункт источника или показать gap `OPT` / pathwise projection / expansion.

### 4.4 Policy и witness — отдельный гейт, но не обязательная атомарная policy-lumpability

Равенство оптимальных значений не гарантирует корректность decoder. Вместе с тем A3 не требует, чтобы одно endpoint-решение реализовывалось одним одинаковым атомарным шагом из всех `c`.

Достаточный конструктивный гейт: parent-path DP → legal endpoint order → вставка `a_j-2` средних копий repeated между first/last → full layout с правильными multiplicities/IDs → независимая проверка **всех** разрезов и достижения `OPT`. Decoder вправе помнить исходные кратности и уже выданные copies. Если API обещает endpoint-only policy без такой памяти, это дополнительный контракт API и отдельный тест, не дописанный нами пункт A3.

Несовпадающие оптимальные witnesses допустимы. Побитовое равенство решений требовать только при заранее заданном общем canonical tie-break. Для основной репликации достаточно равенства целых значений, счётчиков и независимой валидности каждого witness.

## 5. Зафиксированный до нового кода конечный эксперимент K,D,F,M

Это **новый ограниченный протокол аудита**, не область универсальной теоремы и не утверждение, что именно такие границы уже проверены.

| Символ | Значение | Точный смысл |
|---|---:|---|
| `K_max` | 3 | Число различных геометрических классов: `1<=k<=3` |
| `D_max` | 2 | Каждое ambient dimension `d=0,1,2` |
| `F` | `{GF(2),GF(3)}` | Оба поля с обычным представлением вычетов; extension fields не включены |
| `M` | 6 | **Общее** число occurrences: `k<=n=sum(a_j)<=6`; это не максимум каждой кратности |

Геометрия: перечислить все подпространства `GF(p)^d` как множества векторов, включить нулевое и полное в общий список, удалить совпадающие span-sets, упорядочить лексикографически. Взять все `k`-элементные комбинации; каждая отдельная arrangement не обязана содержать оба крайних подпространства. Не факторизовать по `GL(d,p)` и не сэмплировать. Число подпространств для `d=0,1,2` должно быть соответственно `1,2,5` для GF(2) и `1,2,6` для GF(3).

Кратности: для **каждого** `n=k,...,6` перечислить все целочисленные разбиения `n` на `k` положительных частей и **все различные перестановки** частей, назначенные канонически упорядоченным классам. Например, `(1,2,3)` — шесть назначений, `(2,2,2)` — одно. Одного представителя типа «singleton/repeated» недостаточно: именно кратности `>=3` проверяют удаление middle copies. Контроль полноты — все ordered positive vectors с суммой `<=6`; их ровно `C(6,k)`, то есть 6, 15, 20 для `k=1,2,3`.

Ожидаемые **базовые входы**, до дополнительных metamorphic checks:

| Поле | d=0 | d=1 | d=2 | Всего |
|---|---:|---:|---:|---:|
| GF(2) | 6 | 27 | 380 | 413 |
| GF(3) | 6 | 27 | 661 | 694 |
| Всего | 12 | 54 | 1041 | **1107** |

Это расчёт покрытия `sum_{p,d,k} C(number_of_subspaces(p,d),k)*C(6,k)`, **не отчёт о прогоне**. Для каждого входа полный oracle обязан проверить `n!/prod_j a_j!` class-слов, без умножения на перестановки неразличимых копий. Если используются occurrence IDs, проверить корректность перехода к class-словам; width от ID не зависит.

Предопределённые metamorphic checks: для каждого базового входа reverse class labels и, при `d=2`, swap coordinates. Проверить неизменность оптимума и перенос witness; учитывать эти проверки отдельно от 1107 входов. Дополнительные случайные/большие случаи — exploratory, с отдельными seed/границами и без подмены зарегистрированного набора.

Числовой допуск 0. Лимиты: 120 CPU-секунд на базовый вход, включая все его проверки и производные reversal/coordinate-swap runs, 2048 MiB RAM, 24 часа wall time на кампанию. Timeout, crash или пропуск → `INCOMPLETE`, а не PASS. Лимит не является предсказанием производительности. Зафиксировать первый discrepancy сразу; продолжить оставшиеся случаи в бюджете. Один подтверждённый контрпример достаточен для refutation, но «не найден в полном наборе» требует завершения и квалификации всех запланированных проверок; equality от более сильных диагностических свойств не требуется.

## 6. Независимый brute-force oracle и разделение реализаций

Три разных интерфейса предотвращают общую ошибку спецификации:

| Контракт / исполнитель | Что получает и делает | Чего нельзя использовать как основание ответа |
|---|---|---|
| **A. Задача / raw oracle** | Поле, векторы, multiplicities, определение `L_i∩R_i`, цель min–max | q, endpoint transitions, lambda identity и эталонные ответы JANUS |
| **B. Независимый кандидат DP** | Полную математическую спецификацию A3, точный формат I/O | Импорт/переписывание reference implementation, oracle outputs до freeze |
| **C. Adjudicator** | Raw input, allegation, frozen code hashes, оба результата | Принятие alleged values без самостоятельного пересчёта |

Контракт A полностью определён. «Недоопределить спеку в месте леммы» опасно: здесь oracle вообще не получает лемму как предпосылку, а решает исходную конечную задачу напрямую. Поиск минимальной факторизации — возможное дополнительное исследование, не необходимый гейт репликации A3.

Алгоритм oracle:

```text
validate field, dimension, vector entries, positive multiplicities
compute each geometric span as an explicit finite set; reject duplicate classes
enumerate every full multiset word at ORIGINAL a, not only min(a,2)
for every word and EVERY cut i=0..n:
    generate left and right spans by all finite-field linear combinations
    intersect vector sets
    derive integer dimension r from |intersection|=p^r (no floating logarithms)
take maximum per word, minimum across all words
retain a minimizing full word and its entire cut profile
verify number of words equals n!/prod(a_j!)
```

Не переиспользовать linear-algebra helper кандидата. Для маленьких полей можно получить весь список подпространств closure всех подмножеств `GF(p)^d`; при максимуме 9 векторов это конечная независимая конструкция. Отдельно проверить её счётчики §5. Для GF(3) арифметика по модулю 3; XOR допустим только в GF(2).

Параллельно, после code freeze кандидата: полный count-DP (не обязательный oracle, полезная локализация), endpoint-DP, direct width против rank identity, достижимые/coreachable вершины, точные счётчики. Reference DP и его verifier в замороженном пакете полезны как comparison targets, но enumerating endpoint orders через ту же схему переходов и `rho` не заменяет независимый full-occurrence oracle для compression lemma. Пилот §8 этот барьер соблюдает только на одном примере.

Проверять pathwise compression **каждого** full layout, нормализуя support-пары и вычисляя ширины напрямую. Перечислить также **каждый** capped layout и проверить expansion при исходном `a`; правило witness — вставить middle copies непосредственно после первой копии соответствующего repeated class. Проверка дополнительно должна уметь валидировать любой предъявленный lift.

Для continued-state диагностики перечислить все достижимые count vectors; сравнивать q-группы с явно заданными normalized continuations и min–max values. Для задачи без history constraints `c` достаточно, но конкретный сырой suffix должен иметь ровно оставшиеся multiplicities. Strong-bisimulation mismatch сохраняется как диагностический результат, не автоматически как `VALUE`.

Independence подтверждается декларацией автора/организации, датами и списком виденного кода/ответов. Разные процессы, аккаунты, модели и subagents сами по себе внешнюю независимость не устанавливают. Авторы этого brief уже видели A3 sources; будущий clean-room implementer должен отдельно задекларировать exposure. Перед сравнением скрытых ответов он фиксирует hash своей реализации и списка inputs. Корректность oracle проверяется вторым методом/автором и отрицательными контролями; oracle не считается непогрешимым.

Формат входа: UTF-8 JSON с `p,d,classes:[{id,basis}],multiplicities`; каждая basis — список векторов длины d. Для нулевого подпространства basis=`[]`. Canonical input hash: JSON с отсортированными ключами, compact separators, UTF-8, без BOM и без конечного LF; упорядочение classes и basis фиксируется в manifest генератора. Basis выбирается детерминированно из канонического span-set; oracle обязан повторно построить span. Не путать этот input hash с hash pretty-printed preregistration file.

Результат на каждый input: `protocol_sha256,target_sha,input_sha256,implementation_sha256,environment,oracle_optimum,candidate_optimum,state_count,edge_count,witness,cut_widths,coverage,status`. Сохранять timeouts, ошибки и все rejected candidates. Для сравнения значений достаточно точных целых; канонический формат нужен для хеширования, а не для принудительного одинакового tie-break решений.

## 7. Классы контрпримеров и автоматическое решение

| Класс | Что предъявить | Как квалифицировать |
|---|---|---|
| `DOMAIN_OR_NORMALIZATION` | Неверное поле/базисы, совпадающие spans под разными IDs, отсутствующие копии | `REJECTED_OUT_OF_DOMAIN` / `REJECTED_INVALID_INPUT`; не refutation |
| `CUT_IDENTITY` | Валидный cut, direct `dim(L∩R)` и отличный rank result | Подозрение на математику или field/rank code; второй точный пересчёт |
| `PROJECTION` | Full layout, его first/last compression и нарушенное утверждение о support-trace/width | Возможный дефект pathwise lemma; отдельно проверить, нарушен ли optimum |
| `EXPANSION` | Legal endpoint layout и доказанная невозможность требуемого lift | Возможный дефект lemma/decoder; провал одного неудачного decoder ещё не невозможность lift |
| `TRANSITION_OR_REACHABILITY` | Явный пропущенный legal endpoint event либо лишний illegal event | Указать один из трёх графов §3; не считать middle self-loop пропущенным ребром DAG |
| `VALUE` | Полный exhaustive oracle optimum и отличный endpoint-DP optimum на одном валидном входе | После независимого воспроизведения — контрпример к алгоритмическому утверждению / локализация реализации |
| `WITNESS` | Returned path/order/IDs и cut, multiplicity либо precedence defect | Ошибка reconstruction; value и математическое существование lift проверять отдельно |
| `COUNT_OR_COMPLEXITY` | Перечень всех admissible endpoint vertices/edges и расхождение формулы | Счётная часть; benchmark не доказывает асимптотику |
| `STRONG_BISIMULATION_ONLY` | Одна q-пара с разными next-targets или сырыми suffix-языками | Диагностика усиленного свойства; без value/pathwise gap не refutation A3 |
| `WRONG_OBJECTIVE` | Сумма/длина трассы вместо максимума width | `REJECTED_WRONG_OBJECTIVE` |
| `EVIDENCE_OR_PROVENANCE` | Неверный pin/hash, общий код oracle, ложный счётчик или independence claim | Дефект доказательной цепочки; не автоматически математическая ложность |
| `PRIOR_ART` | Точный DOI/arXiv/theorem и отображение гипотез/вывода | Только параллельный novelty-трек |

Adjudication: (1) закрепить allegation/raw input до исправлений; (2) проверить domain и hashes; (3) независимо пересчитать исходный полный optimum и обе стороны alleged gap; (4) проверить layout legality, все cuts, полноту перебора и целевую функцию; (5) попытаться минимизировать по фиксированному порядку `p,d,k,n,a,geometry,layout`; (6) независимо перепроверить уменьшенный input; (7) опубликовать accepted/rejected/inconclusive с причиной. Отсутствие воспроизведения из-за ошибки окружения — `INCONCLUSIVE`, не математическое отклонение.

Два layout с разной шириной не устанавливают разность **оптимумов**. Нужно точное перечисление или независимо проверяемые lower/upper certificates. Ошибку конкретной реализации не объявлять опровержением теоремы, пока не проверена сама mathematical compression/DP specification. Pathwise lemma и optimum theorem также имеют разные области refutation.

После положительного прохода формулировка только: «В полном зарегистрированном конечном наборе с указанными hash контрпример не найден». Для доказательства с неограниченными `k,d,F,a` нужна математическая аргументация, отдельно проверенная. Перечень конечных выживших тестов её не заменяет.

## 8. Выполненный dry run ложного контрпримера

**Предварительный exploratory negative control, выполненный до preregistration.** Он не входит в заявленные 1107 confirmatory cases и не используется для продвижения A3. Созданный отдельно в этой сессии проверяющий не импортирует JANUS, не использует q для вычисления optimum, rank identity или endpoint transitions. Он строит spans как явные XOR-замкнутые множества векторов.

Вход: `GF(2)^2`, `U_1=span((1,0))`, `U_2=span((0,1))`, `a=(3,1)`, capped `b=(2,1)`. Намеренно ложное allegation: `OPT_full=2`, `OPT_capped=1`.

| Фактическая проверка | Full (3,1) | Capped (2,1) |
|---|---:|---:|
| Все legal class-слова | 4 | 3 |
| Все проверенные cuts, включая границы | 20 | 12 |
| Вычисленный exact optimum | **1** | **1** |

Полные слова и фактические cut widths:

```text
1112: [0,1,1,0,0]    112: [0,1,0,0]
1121: [0,1,1,1,0]    121: [0,1,1,0]
1211: [0,1,1,1,0]    211: [0,0,1,0]
2111: [0,0,1,1,0]
```

Автоматический результат — `REJECTED_FALSE_COUNTEREXAMPLE`: заявленное full value 2 неверно. Дополнительные forged layouts `112` и `11112`, предъявленные как full `(3,1)`, отклонены как `REJECTED_INVALID_LAYOUT` из-за нехватки/избытка копии.

Одновременно q-пара `c=(1,0)` и `c'=(2,0)` демонстрирует провал naive strong one-step bisimulation: next class-1 target — Active против Done. Условие оптимальной стоимости в этом примере сохраняется. Это проверяет, что процедура не повышает mismatch усиленного свойства до refutation A3.

```text
pilot checker SHA-256 = a4443fb804f17c5c3f00738b604d1754b252b7a9d6127cdbd576e18a959adb98
pilot receipt SHA-256 = d544d48a1b8b88f4c9f91bba12365976d4e286eb731e8d834b991ab392c17197
canonical pilot input SHA-256 = 1fc6b1eb910e2c86c1510fbee561222c81d1d4c8416e37d143571a85cb60c674
```

Приложение B воспроизводит точный исходный Python-файл; сохранить его как UTF-8 без BOM, LF, с одним конечным LF. Команда `python reject_false_counterexample.py` создаёт `receipt.json` рядом с файлом. Окружение пилота: Python 3.14.2, MSC v.1944 64 bit AMD64, Windows build 10.0.19045; только стандартная библиотека. Отдельное внешнее окружение не проверено. В приложении C содержится полный первоначальный receipt. При изменении bytes/переносов строк hash изменится; это не само по себе математическое расхождение.

Независимость здесь означает отдельно написанный автоматический checker по raw semantics в рамках одной сессии. **Внешняя независимость, blinded clean-room и universal correctness не установлены.**

## 9. Три параллельных трека статусов

Статусы записывать к конкретному объекту и SHA. Они не образуют общую лестницу: продвижение одного трека не повышает остальные.

| Трек | Ступени / гейты | Состояние при подготовке brief |
|---|---|---|
| **C — корректность / фальсификация** | `PROTOCOL_FROZEN` → `FINITE_AUDIT_COMPLETE_NO_REFUTATION` либо `COUNTEREXAMPLE_PENDING` → `COUNTEREXAMPLE_INDEPENDENTLY_REPRODUCED`; отдельно `SCOPED_PROOF_REVIEWED` | Новая кампания `NOT_RUN`; negative control §8 выполнен. Репозиторий заявляет ES5 admission; новый внешний proof review не выполнен |
| **R — воспроизводимость / независимость** | `SELF_VERIFIED` → `EXTERNALLY_INSPECTED` (другой человек запускает reference) → `INDEPENDENTLY_REPLICATED` (своя реализация + raw oracle, заявленные scope/exposure) | `EXTERNAL_INDEPENDENT_REPLICATION=NOT_ESTABLISHED`. Пилот — same-session procedural check. Cross-runner PDF PASS относится только к build |
| **N — новизна / prior art** | Declared search → `N3_NOVELTY_CANDIDATE` → external exact-equivalence/direct-subsumption review; outcomes `PRIOR_ART_SUBSUMES`, narrowed claim, либо обоснованная ограниченная novelty оценка | Источники заявляют N3; собственный новый literature audit не выполнен; `WORLD_NOVELTY_N4=NOT_ESTABLISHED` |

`EXTERNALLY_VALIDATED` без уточнения использовать нельзя: указать expert, объект, scope, report и ограничения — correctness review это или bibliographic/novelty review. Clean-room совпадение в конечном наборе устанавливает воспроизводимость на этом наборе; не доказывает универсальную lemma и не устанавливает мировой приоритет. И наоборот, prior art может лишить новизны корректную A3, не создав value counterexample.

Внешние участники работают параллельно: C атакует full semantics/proof; R пишет/запускает реализации с декларацией независимости; N ищет exact/directly subsuming результаты. Общий evidence ledger хранит hashes и отчёты, но verdict каждого трека публикуется отдельно. Никому не отправлялись письма или приглашения от имени пользователя.

## 10. Pre-registration, crypto commitment и порядок release

Нормативный объект — **точные bytes** `A3_REFUTATION_PREREGISTRATION_V1.json` из приложения A: UTF-8 без BOM, LF, sorted keys, indent=2 и один конечный LF. Его SHA-256:

```text
93411c043dfe6058a652a0df75bff8aa3dd2216b8d5e1c5503755f30bd9729ae
```

Объект фиксирует bounds, полное покрытие, objective, independent oracle, минимальный порог discrepancy=1, нулевой допуск, бюджеты, остановку, negative/incomplete outcomes, exposure и amendment policy. Он не содержит результатов будущего confirmatory run.

**Публикационный порядок этой поставки:** сначала отдельный immutable commit с корректными preregistration JSON bytes и hash в commit message, затем опубликован checksum, затем commit с этим brief, включая pilot source. Никакой новой реализации полной A3-кампании не публикуется. Пилот уже выполнен exploratory; более поздний hash не переименовывает его в заранее зарегистрированный эксперимент. Первоначальный reference code A3 также уже публичен, поэтому сделать commitment «до любого кода A3 в истории» невозможно и здесь не заявляется.

Открытая запись исправления: первый транспортный commit `1adf9c9cb5b99bd8f43ceaed3fd8e17b82b85be0` получил CRLF вместо LF, и его фактический digest `ad4f2424f512cfd807e45edddd217cff39d116f4b2d1657ae4f8eb96c322e182` не совпал с заявленным. Он сохранён в истории как **rejected transport attempt**. Исправленная registration revision 1.0.1 содержит ссылку на него и причину; семантические параметры не менялись, кампания между попытками не запускалась, pilot source не публиковался. У корректного protocol commit удалённые bytes непосредственно сравнены с локальными и совпали; hash также совпал. История не переписана.

Протокольный commit: [1e663b1281d148e1fdba2f6ecf91b61144efaf40](https://github.com/Hawkar-usls/Janus-Fundamentum/commit/1e663b1281d148e1fdba2f6ecf91b61144efaf40). Публичный commit даёт проверяемую привязку содержимого и порядок публикации. Git author/committer time сам по себе не является доверенным временем; для независимого timestamp рекомендуется countersigned archive / RFC 3161 или аналогичный внешний witness. Такой независимый timestamp **не получен**. Внешняя регистрация/acceptance протокола **не установлена**; статус — опубликованный protocol commitment в изолированном PR.

Для следующего исследователя порядок обязателен:

1. Скачать preregistration по immutable commit, проверить SHA-256 и сделать собственную датированную копию до просмотра answers / release своего research code. Зафиксировать, какие sources/outputs уже видел.
2. До сравнения с reference/oracle outcomes заморозить свою реализацию, field library/environment, generator, полный input manifest и их SHA-256; раздельно подписать exposure statement oracle author и DP author.
3. Запустить полный набор; опубликовать exact coverage и все discrepancies/timeouts, raw witnesses/cuts и adjudication, даже при отрицательном результате.
4. Выпустить код и receipts с immutable links; сравнивать результаты только в заявленном scope. Идентичность output bytes допустима как дополнительная проверка канонических полей, не как доказательство A3.
5. Для изменения границ/объектива/лимитов/кода после просмотра результатов создать v2 с parent hash, причиной, временем и exposure. Старые v1 bytes сохраняются. Новые exploratory cases не становятся confirmatory задним числом.

Hash идентифицирует bytes и изменение версии. Он не доказывает truth, авторство/независимость, полноту поиска, отсутствие скрытого предварительного просмотра или универсальную novelty. Отдельный `A3_REFUTATION_BRIEF.sha256` закрепляет итоговый документ; его собственный digest не вставлен в файл во избежание циклического само-хеширования.

## 11. Конкретное задание следующему независимому проверяющему

Передать этот brief, frozen source links и preregistration hash. Попросить две отдельно фиксируемые поставки: raw exhaustive oracle по контракту A и самостоятельно написанный DP по контракту B; допускаются разные авторы. Не передавать reference implementation автору DP до его code freeze. Материалы задачи/теоремы полностью определены; код кандидата, эталонные outputs и verdicts остаются за гейтом exposure.

Обязательный итоговый report:

```text
TARGET_CLAIM / TARGET_SHA / PROTOCOL_SHA256
AUTHOR / AFFILIATION / EXPOSURE / INDEPENDENCE_LIMITS
IMPLEMENTATION_HASHES / RUNTIME / DEPENDENCIES
K,D,F,M / EXPECTED_AND_ACTUAL_COVERAGE
ORACLE_METHOD / COMPLETENESS_COUNTS
OPT_COMPARISON / PROJECTION / EXPANSION / REACHABILITY
WITNESS_VALIDATION / NEGATIVE_CONTROLS
ALL_ACCEPTED_AND_REJECTED_CANDIDATES
TIMEOUTS_CRASHES_AND_AMENDMENTS
CORRECTNESS_STATUS / REPLICATION_STATUS / NOVELTY_STATUS
IMMUTABLE_ARTIFACT_LINKS / NEXT_UNRESOLVED_GATE
```

В PR этой поставки добавляются только новые документы/JSON/checksums в отдельной ветке; reference algorithms, theorem/admission objects, issue #173 и Meta Registry не изменяются. PR не сливается автоматически. Коммит протокола и итоговый diff позволяют проверить изоляцию.

## 12. Что остаётся непроверенным

- Полная конечная кампания 1107 inputs и metamorphic schedule не запускалась; её outputs, candidate DP и confirmatory code ещё не созданы.
- Новый универсальный математический proof review, внешний clean-room implementer и независимый adjudication реального контрпримера отсутствуют.
- Поля кроме GF(2)/GF(3), `d>2`, `k>3`, `n>6` не покрываются этим конечным протоколом; сама A3 заявляет значительно более широкую область.
- Timing, bit complexity, стоимость чтения кратностей и развёрнутого witness не следуют из счётчика `O(k*3^k)`. Этот счётчик относится к combinatorial DP после rank preprocessing. Чтение входа/полевые операции учитываются отдельно; выдача полного layout требует как минимум `Ω(n)` вывода.
- Производительность новых реализаций, расширенные field libraries, полный replay CI/PDF, cross-environment build и новая мировая literature novelty не проверены.
- Пилот подтверждает работу отрицательного контроля на одном входе; его создание разными агентами одной сессии не даёт внешней независимости.

Потолки сохраняются: `EXTERNAL_INDEPENDENT_REPLICATION=NOT_ESTABLISHED`, `WORLD_NOVELTY_N4=NOT_ESTABLISHED`, `P_VS_NP=OPEN`. Достижение этой поставки — проверяемый протокол и отрицательный контроль с источниками, границами и правилом честного verdict.

## Приложение A. Нормативная preregistration revision 1.0.1

Содержимое блока, включая один конечный LF перед закрывающей оградой, совпадает с JSON protocol commit.

```json
{
  "amendments": "New version plus parent hash, reason, time and exposure statement; never rewrite the old registration or relabel exploratory results as preregistered.",
  "bounds": {
    "D_max_ambient_dimension": 2,
    "F_prime_fields": [
      2,
      3
    ],
    "K_max_distinct_classes": 3,
    "M_max_total_occurrences": 6
  },
  "budget": {
    "campaign_wall_hours": 24,
    "cpu_seconds_per_base_instance": 120,
    "derived_runs_accounting": "The per-base CPU budget includes all checks and its reversal/coordinate-swap derived runs.",
    "on_timeout": "INCOMPLETE_NOT_PASS; no skipped case silently counted as agreement",
    "ram_mib": 2048
  },
  "candidate_acceptance": "A valid, in-domain mismatch must be recomputed by a separately authored checker from raw input; invalid or stronger-property-only allegations are rejected with reasons.",
  "ceilings": {
    "external_independent_replication": "NOT_ESTABLISHED",
    "finite_agreement_is_universal_proof": false,
    "p_vs_np": "OPEN",
    "world_novelty_n4": "NOT_ESTABLISHED"
  },
  "checks": [
    "domain",
    "all_full_layouts_and_cuts",
    "all_full_to_capped_projections",
    "all_capped_layouts_and_expansions",
    "independent_endpoint_dp",
    "state_and_edge_counts",
    "direct_width_vs_rank_identity",
    "witness_multiplicities_and_all_cuts",
    "reachable_and_coreachable_states",
    "same_endpoint_continuations_diagnostic"
  ],
  "continuation_diagnostic": "Within each fixed input and every reachable count-vector q-group, compare endpoint-event trace languages with class ID and atom/start/finish labels after suppressing q-stutters, and their max-width costs. Raw suffix-language and exact atomic strong-bisimulation failures are classified diagnostics, not automatic A3 value failures.",
  "domain": "For each p in F, d=0..D, k=1..K: all k-element sets of pairwise distinct subspaces of GF(p)^d; include zero and full subspaces.",
  "equivalent_profile_check": "All ordered positive vectors a with sum(a)<=M; for fixed k there must be binomial(M,k) vectors.",
  "expansion_rule": "For every capped layout perform one canonical expansion: insert a_j-2 middle copies immediately after class j first endpoint; verify every cut and original multiplicities. All full layouts are separately covered by projection checks.",
  "expected_base_instances": 1107,
  "expected_base_instances_by_p_d": {
    "2,0": 6,
    "2,1": 27,
    "2,2": 380,
    "3,0": 6,
    "3,1": 27,
    "3,2": 661
  },
  "expected_subspace_counts_by_d": {
    "2": [
      1,
      2,
      5
    ],
    "3": [
      1,
      2,
      6
    ]
  },
  "fundamentum_navigation_sha": "76de4c084a178fdaef7576b7128be36486072e76",
  "geometry_enumeration": "All subspaces as explicit vector sets, lexicographically sorted; zero and full belong to the universe, not necessarily every selected arrangement; all k-combinations; no GL(d,p) quotient and no geometric sampling.",
  "meta_registry_sha": "556424f457272d78a614642d8022c4e81c57929c",
  "metamorphic_schedule": "For every base instance also reverse class labels and, when d=2, swap vector coordinates; compare invariant optima and validate remapped witnesses. Log separately from 1107 base instances.",
  "minimization_order": "p,d,k,total_occurrences,ordered_multiplicity_vector,canonical_geometry,layout lexicographic; every reduction independently rechecked.",
  "multiplicity_enumeration": "For n=k..M enumerate every integer partition of n into k positive parts and every distinct assignment/permutation of those parts to the canonically ordered classes.",
  "numeric_tolerance": 0,
  "oracle": "Enumerate all full multiset class words at original multiplicities; evaluate every cut by explicit left/right vector-set spans and intersection cardinality; no q, endpoint transition code, rank identity, JANUS import or reference outputs.",
  "pilot_status": "EXPLORATORY_NEGATIVE_CONTROL_COMPLETED_BEFORE_PREREGISTRATION",
  "prepared_date_local": "2026-11-14",
  "protocol_id": "A3_REFUTATION_BRIEF_V1",
  "randomness": "NONE_IN_CONFIRMATORY_CAMPAIGN",
  "registration_revision": "1.0.1",
  "release_order": [
    "publish exact preregistration UTF-8 LF bytes and SHA-256 commitment in immutable commit",
    "archive commit URL and timestamp; obtain independent timestamp/countersignature if possible",
    "independent implementer freezes code and fixture manifest before seeing reference outputs",
    "publish implementation and run receipts, including negative and incomplete results"
  ],
  "required_mismatch_count_for_candidate": 1,
  "required_receipt_fields": [
    "protocol_sha256",
    "target_sha",
    "input_sha256",
    "implementer_and_exposure_declaration",
    "implementation_sha256",
    "environment",
    "completed_coverage",
    "timeouts",
    "crashes",
    "all_discrepancies",
    "oracle_optimum",
    "candidate_optimum",
    "full_witness",
    "all_cut_widths"
  ],
  "schema": "janus.a3.refutation.preregistration.v1",
  "stop_rule": "Preserve the first discrepancy and minimal reproduction immediately; continue in-domain cases if budget permits. A complete no-refutation report requires every scheduled check completed and adjudicated, not equality in stronger-property diagnostics; a validated refutation needs one case.",
  "study_status_at_freeze": "NOT_STARTED",
  "target_publication_sha": "811d954e52296893898062d9abea7aaf572629be",
  "timezone": "Europe/Kiev",
  "transport_correction": {
    "actual_rejected_bytes_sha256": "ad4f2424f512cfd807e45edddd217cff39d116f4b2d1657ae4f8eb96c322e182",
    "intended_previous_lf_sha256": "409a4ae72c8511252ca8806bfd2433d54deb8836713a5c18145b0f456a457824",
    "reason": "Windows stdout changed LF to CRLF before the first GitHub upload. The declared digest did not match published bytes. Previous immutable commit is retained as a rejected transport attempt; no campaign ran and no pilot source was released between attempts.",
    "rejected_commit": "1adf9c9cb5b99bd8f43ceaed3fd8e17b82b85be0",
    "semantic_protocol_change": false
  }
}
```

## Приложение B. Исполнимый exploratory negative-control checker

Сохранить содержимое блока в `reject_false_counterexample.py` (UTF-8 без BOM, LF, один конечный LF) и выполнить `python reject_false_counterexample.py`. Это пилот, не код полной кампании.

```python
"""Tiny A3 negative-control checker, authored from raw set-span semantics.

No JANUS implementation, endpoint DP, or subset-rank identity is imported.
This is a same-session checker; it is not external scientific replication.
"""

from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def span_xor(generators, dimension):
    """Construct every vector of the GF(2) span, explicitly."""
    vectors = {(0,) * dimension}
    for generator in generators:
        if len(generator) != dimension or any(x not in (0, 1) for x in generator):
            raise ValueError("invalid GF(2) vector")
        vectors |= {tuple(a ^ b for a, b in zip(v, generator)) for v in tuple(vectors)}
    return vectors


def dimension_from_size(vectors):
    size = len(vectors)
    if size == 0 or size & (size - 1):
        raise ValueError("span cardinality is not a positive power of two")
    return size.bit_length() - 1


def validate_word(word, multiplicities):
    expected = Counter({j + 1: count for j, count in enumerate(multiplicities)})
    observed = Counter(word)
    if observed != expected:
        raise ValueError("occurrence multiset mismatch")


def cut_profile(word, bases, multiplicities, ambient_dimension):
    validate_word(word, multiplicities)
    profile = []
    for cut in range(len(word) + 1):
        left = span_xor([v for j in word[:cut] for v in bases[j - 1]], ambient_dimension)
        right = span_xor([v for j in word[cut:] for v in bases[j - 1]], ambient_dimension)
        intersection = left & right
        profile.append(dimension_from_size(intersection))
    return profile


def all_words(multiplicities):
    # Enumerate the entire product, retaining exactly the prescribed multiset.
    # Tiny deliberately inefficient oracle, independent of endpoint transitions.
    length = sum(multiplicities)
    expected = Counter({j + 1: count for j, count in enumerate(multiplicities)})
    return [word for word in product(range(1, len(multiplicities) + 1), repeat=length)
            if Counter(word) == expected]


def exhaustive_result(bases, multiplicities, ambient_dimension):
    rows = []
    for word in all_words(multiplicities):
        profile = cut_profile(word, bases, multiplicities, ambient_dimension)
        rows.append({"word": list(word), "cut_widths": profile, "width": max(profile)})
    if not rows:
        raise ValueError("no legal layouts")
    return {
        "multiplicities": list(multiplicities),
        "legal_order_count": len(rows),
        "total_cuts_checked": sum(len(row["cut_widths"]) for row in rows),
        "optimum": min(row["width"] for row in rows),
        "layouts": rows,
    }


def endpoint_status(counts, multiplicities):
    return ["NotStarted" if c == 0 else "Done" if c == m else "Active"
            for c, m in zip(counts, multiplicities)]


def main():
    fixture = {
        "field": "GF(2)",
        "ambient_dimension": 2,
        "bases": [[[1, 0]], [[0, 1]]],
        "multiplicities": [3, 1],
    }
    bases = fixture["bases"]
    multiplicities = fixture["multiplicities"]
    dimension = fixture["ambient_dimension"]
    full = exhaustive_result(bases, multiplicities, dimension)
    capped = exhaustive_result(bases, [min(m, 2) for m in multiplicities], dimension)
    allegation = {"full_optimum": 2, "capped_optimum": 1, "relation": "different"}
    agrees_with_allegation = (full["optimum"] == allegation["full_optimum"]
                              and capped["optimum"] == allegation["capped_optimum"]
                              and full["optimum"] != capped["optimum"])
    verdict = "COUNTEREXAMPLE_REPRODUCED" if agrees_with_allegation else "REJECTED_FALSE_COUNTEREXAMPLE"
    invalid_controls = []
    for label, word in [("missing_occurrence", [1, 1, 2]),
                        ("extra_occurrence", [1, 1, 1, 1, 2])]:
        try:
            cut_profile(word, bases, multiplicities, dimension)
        except ValueError as exc:
            invalid_controls.append({"case": label, "word": word,
                                     "verdict": "REJECTED_INVALID_LAYOUT", "reason": str(exc)})
        else:
            raise AssertionError("invalid-layout control failed open")

    state_a = [1, 0]
    state_b = [2, 0]
    after_a = [2, 0]
    after_b = [3, 0]
    assert endpoint_status(state_a, multiplicities) == endpoint_status(state_b, multiplicities)
    assert endpoint_status(after_a, multiplicities) != endpoint_status(after_b, multiplicities)
    assert verdict == "REJECTED_FALSE_COUNTEREXAMPLE"
    assert full["optimum"] == capped["optimum"] == 1
    assert full["legal_order_count"] == 4 and capped["legal_order_count"] == 3

    script_hash = sha256(Path(__file__).read_bytes()).hexdigest()
    fixture_bytes = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt = {
        "schema": "a3.false_counterexample_dry_run.v1",
        "scope": "Only this explicit fixture; no general A3 verdict, no external replication claim.",
        "checker_independence": "Separately authored same-session checker; raw explicit vector-set spans; no JANUS code imported.",
        "script_sha256": script_hash,
        "fixture_sha256_canonical_json": sha256(fixture_bytes).hexdigest(),
        "fixture": fixture,
        "deliberately_false_allegation": allegation,
        "full_oracle": full,
        "capped_oracle": capped,
        "verdict": verdict,
        "rejection_reason": "The full and capped exhaustive optima both equal 1; the alleged full optimum 2 is false.",
        "invalid_layout_controls": invalid_controls,
        "one_step_bisimulation_diagnostic": {
            "state_a": state_a,
            "state_b": state_b,
            "common_endpoint_status": endpoint_status(state_a, multiplicities),
            "same_action": "process one occurrence of class 1",
            "after_a_endpoint_status": endpoint_status(after_a, multiplicities),
            "after_b_endpoint_status": endpoint_status(after_b, multiplicities),
            "verdict": "NAIVE_STRONG_ONE_STEP_BISIMULATION_FAILS",
            "a3_implication": "Not an A3 refutation: endpoint compression may remove middle-occurrence stutters; exact bottleneck optima here agree.",
        },
    }
    output_path = Path(__file__).with_name("receipt.json")
    output_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "full_optimum": full["optimum"],
                      "capped_optimum": capped["optimum"], "full_orders": full["legal_order_count"],
                      "capped_orders": capped["legal_order_count"], "script_sha256": script_hash,
                      "receipt_sha256": sha256(output_path.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
```

## Приложение C. Первоначальный pilot receipt

В этом читаемом блоке JSON переносы отображены как LF. У первоначального receipt, созданного на Windows, все переносы CRLF; приведённый в §8 hash относится к этим исходным bytes. Для точного восстановления сохранить блок с CRLF и одним конечным CRLF. Смысл JSON от переносов не зависит. Повторный запуск на другой ОС может дать иной byte hash receipt без изменения математического результата.

```json
{
  "capped_oracle": {
    "layouts": [
      {
        "cut_widths": [
          0,
          1,
          0,
          0
        ],
        "width": 1,
        "word": [
          1,
          1,
          2
        ]
      },
      {
        "cut_widths": [
          0,
          1,
          1,
          0
        ],
        "width": 1,
        "word": [
          1,
          2,
          1
        ]
      },
      {
        "cut_widths": [
          0,
          0,
          1,
          0
        ],
        "width": 1,
        "word": [
          2,
          1,
          1
        ]
      }
    ],
    "legal_order_count": 3,
    "multiplicities": [
      2,
      1
    ],
    "optimum": 1,
    "total_cuts_checked": 12
  },
  "checker_independence": "Separately authored same-session checker; raw explicit vector-set spans; no JANUS code imported.",
  "deliberately_false_allegation": {
    "capped_optimum": 1,
    "full_optimum": 2,
    "relation": "different"
  },
  "fixture": {
    "ambient_dimension": 2,
    "bases": [
      [
        [
          1,
          0
        ]
      ],
      [
        [
          0,
          1
        ]
      ]
    ],
    "field": "GF(2)",
    "multiplicities": [
      3,
      1
    ]
  },
  "fixture_sha256_canonical_json": "1fc6b1eb910e2c86c1510fbee561222c81d1d4c8416e37d143571a85cb60c674",
  "full_oracle": {
    "layouts": [
      {
        "cut_widths": [
          0,
          1,
          1,
          0,
          0
        ],
        "width": 1,
        "word": [
          1,
          1,
          1,
          2
        ]
      },
      {
        "cut_widths": [
          0,
          1,
          1,
          1,
          0
        ],
        "width": 1,
        "word": [
          1,
          1,
          2,
          1
        ]
      },
      {
        "cut_widths": [
          0,
          1,
          1,
          1,
          0
        ],
        "width": 1,
        "word": [
          1,
          2,
          1,
          1
        ]
      },
      {
        "cut_widths": [
          0,
          0,
          1,
          1,
          0
        ],
        "width": 1,
        "word": [
          2,
          1,
          1,
          1
        ]
      }
    ],
    "legal_order_count": 4,
    "multiplicities": [
      3,
      1
    ],
    "optimum": 1,
    "total_cuts_checked": 20
  },
  "invalid_layout_controls": [
    {
      "case": "missing_occurrence",
      "reason": "occurrence multiset mismatch",
      "verdict": "REJECTED_INVALID_LAYOUT",
      "word": [
        1,
        1,
        2
      ]
    },
    {
      "case": "extra_occurrence",
      "reason": "occurrence multiset mismatch",
      "verdict": "REJECTED_INVALID_LAYOUT",
      "word": [
        1,
        1,
        1,
        1,
        2
      ]
    }
  ],
  "one_step_bisimulation_diagnostic": {
    "a3_implication": "Not an A3 refutation: endpoint compression may remove middle-occurrence stutters; exact bottleneck optima here agree.",
    "after_a_endpoint_status": [
      "Active",
      "NotStarted"
    ],
    "after_b_endpoint_status": [
      "Done",
      "NotStarted"
    ],
    "common_endpoint_status": [
      "Active",
      "NotStarted"
    ],
    "same_action": "process one occurrence of class 1",
    "state_a": [
      1,
      0
    ],
    "state_b": [
      2,
      0
    ],
    "verdict": "NAIVE_STRONG_ONE_STEP_BISIMULATION_FAILS"
  },
  "rejection_reason": "The full and capped exhaustive optima both equal 1; the alleged full optimum 2 is false.",
  "schema": "a3.false_counterexample_dry_run.v1",
  "scope": "Only this explicit fixture; no general A3 verdict, no external replication claim.",
  "script_sha256": "a4443fb804f17c5c3f00738b604d1754b252b7a9d6127cdbd576e18a959adb98",
  "verdict": "REJECTED_FALSE_COUNTEREXAMPLE"
}
```
