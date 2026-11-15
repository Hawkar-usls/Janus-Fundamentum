# A3_REFUTATION_BRIEF

**Версия brief 2.0 · registration revision 2.0.0 · 14 ноября 2026 · язык проверки: точная конечная арифметика.**

Практический протокол независимой попытки опровергнуть **замороженную** A3 endpoint-compression / ternary-DP theorem. Документ фиксирует объект проверки, конечный эксперимент, критерии контрпримера, разделение статусов и порядок публикации. Он не объявляет ни доказательство A3, ни её опровержение, ни внешнюю репликацию. Полный зарегистрированный эксперимент **ещё не выполнен**. Отдельно описаны предварительный отрицательный контроль (§8) и пять структурных count-проб (§5.1); они не засчитываются как выполнение кампании 1107 входов.

Нормативные параметры и критерии adjudication приведены в приложении A; первоначальный исполнимый пилот и его результат — в приложениях B–C; count-checker и его receipt — в приложениях D–E; отдельный контракт исходной задачи — в приложении F. Это единый brief с приложениями. V1 preregistration сохранена; v2 явно усиливает протокол до полной кампании, после раскрытого пилота и до первого запуска count-checker.

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

## 5. Зафиксированный до полной кампании конечный эксперимент K,D,F,M

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

### 5.1 Отдельная проверка счётчиков: разные (s,r), без подмены optimum

Первоначальный value-пилот `(3,1)` против `(2,1)` не проверял формулу числа состояний/рёбер. Оба профиля имеют `s=1,r=1`; одинаковые формульные ожидания 6/7 следуют из той же saturation-категории. Результат optimum 1/1 касается одного compression-примера и отрицательного контроля, а не счётчиков.

V2 до первого запуска count-checker фиксирует отдельные **структурные** пробы:

| Кратности | s | r | Ожидаемые admissible states | Ожидаемые unique directed edges |
|---|---:|---:|---:|---:|
| `(3,1)` | 1 | 1 | 6 | 7 |
| `(2,1)` | 1 | 1 | 6 | 7 |
| `(2,2)` | 0 | 2 | 9 | 12 |
| `(1,1)` | 2 | 0 | 4 | 4 |
| `(1,1,1)` | 3 | 0 | 8 | 12 |

Observed counts получать **из явно построенных множеств**, а не вычислением проверяемой формулы: literal product состояний singleton NotStarted/Done и repeated NotStarted/Active/Done; каждое legal atom/start/finish ребро; отдельные forward/reverse BFS. Сохранить все вершины и unique edges. Геометрия, width filter и occurrence middle-copy self-loops в этот полный DAG не входят. На этих unrestricted графах все admissible vertices должны быть reachable и co-reachable.

Заранее фиксируются три tamper-контроля на каждую пробу: удалить legal edge, добавить illegal sink→source edge, изменить ожидаемый vertex count. Все 15 должны быть отклонены. Результат этих проб: **все пять literal counts совпали с таблицей; все 15 tamper-контролей отклонены; forward/reverse BFS подтвердили полную reachability/co-reachability**. Запуск выполнен после V2 commit/digest; source и полный receipt находятся в приложениях D–E.

Граница результата: это проверка собственного literal count-harness, `SELF_VERIFIED`. Будущий DP обязан выдать **свои фактически созданные/admissible/reachable вершины и набор legal transitions**, сравниваемые с literal sets по этим пяти профилям и всем входам кампании. Выделять capacity памяти, admissible states, actually visited states и количество relaxation attempts отдельно. Данный standalone checker reference-DP не запускал; соответствующий DP-instrumentation gate остаётся `NOT_RUN`. Пять совпадений не доказывают общую формулу. Полная кампания остаётся `NOT_RUN`.

## 6. Независимый brute-force oracle и разделение реализаций

Три разных интерфейса предотвращают общую ошибку спецификации:

| Контракт / исполнитель | Что получает и делает | Чего нельзя использовать как основание ответа |
|---|---|---|
| **A. Задача / raw oracle** | Поле, векторы, multiplicities, определение `L_i∩R_i`, цель min–max | q, endpoint transitions, lambda identity и эталонные ответы JANUS |
| **B. Независимый кандидат DP** | Полную математическую спецификацию A3, точный формат I/O | Импорт/переписывание reference implementation, oracle outputs до freeze |
| **C. Mathematical reviewer** | Полную исходную задачу и точное проверяемое утверждение; frozen proof скрыт до фиксации собственной аргументации, если заявляется независимый вывод | Подмена собственного вывода переписыванием готового proof |
| **D. Adjudicator** | Raw input, allegation, frozen code hashes, оба результата | Принятие alleged values без самостоятельного пересчёта и независимой проверки роли источника |

Контракт A полностью определён. Для его передачи создан отдельный `A3_RAW_ORACLE_CONTRACT_V2.md` (приложение F): он не содержит q, compression lemma, endpoint recurrence, rank identity или ожидаемых optimum. Автор raw oracle получает **этот пакет отдельно, не общий brief**. Читать общий brief и затем заявлять blindness к сжатию нельзя. Oracle не обязан выводить сжатие: он решает исходную задачу без него.

Контракт B намеренно содержит полную спецификацию endpoint-алгоритма. Такой clean-room проверяет самостоятельную реализацию известного алгоритма; он не считается независимым открытием или доказательством compression lemma. Для независимого вывода леммы предназначена роль C: исходная задача плюс явно проверяемый тезис, с фиксацией собственной аргументации до чтения готового proof. Неопределённость необходимого определения задачи не является достоинством спеки. Независимость от леммы достигается отсутствием этой леммы в предпосылках raw oracle, а не неполнотой исходной задачи.

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

Independence подтверждается декларацией автора/организации, датами и списком виденного кода/ответов. Разные процессы, аккаунты, модели и subagents сами по себе внешнюю независимость не устанавливают. Отдельно фиксировать code independence, author/exposure independence и external independence. Все выполненные в этой сессии value/count-проверки имеют только `SELF_VERIFIED` для результата; «написан отдельно» не даёт даже `EXTERNALLY_INSPECTED`. Авторы этого brief уже видели A3 sources; будущий clean-room implementer должен отдельно задекларировать exposure. Перед сравнением скрытых ответов он фиксирует hash своей реализации и списка inputs. Корректность oracle проверяется вторым методом/автором и отрицательными контролями; oracle не считается непогрешимым.

Формат входа: UTF-8 JSON с `p,d,classes:[{id,basis}],multiplicities`; каждая basis — список векторов длины d. Для нулевого подпространства basis=`[]`. Canonical input hash: JSON с отсортированными ключами, compact separators, UTF-8, без BOM и без конечного LF; упорядочение classes и basis фиксируется в manifest генератора. Basis выбирается детерминированно из канонического span-set; oracle обязан повторно построить span. Не путать этот input hash с hash pretty-printed preregistration file.

Результат на каждый input: `protocol_sha256,target_sha,input_sha256,implementation_sha256,environment,oracle_optimum,candidate_optimum,state_count,edge_count,witness,cut_widths,coverage,status`. Сохранять timeouts, ошибки и все rejected candidates. Для сравнения значений достаточно точных целых; канонический формат нужен для хеширования, а не для принудительного одинакового tie-break решений.

## 7. Классы контрпримеров и автоматическое решение

| Класс | Что предъявить | Как квалифицировать |
|---|---|---|
| `DOMAIN_OR_NORMALIZATION` | Невалидное поле/базисы, совпадающие spans под разными IDs, отсутствующие копии | Проверить область самой теоремы отдельно от ограничений кампании; только действительно невалидный input отклоняется |
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

### 7.1 Нормативная граница refutation / non-refutation, замороженная V2

Следующие правила находятся в **самом V2 preregistration JSON**, а не выводятся из последующей интерпретации brief. Все числовые контрпримеры в этой таблице **гипотетические иллюстрации критериев**, не найденные результаты. Один mismatch открывает `CANDIDATE_PENDING`. После независимого подтверждения квалифицируется конкретный пункт источника и отдельно — его последствия для других пунктов.

| Claim ID | Что считается refutation названного утверждения | Что одного этого НЕ следует |
|---|---|---|
| `REF_SUPPORT_TRACE` | Один legal full layout и его точное first/last deletion имеют разные нормализованные support-pair traces | Неравенство глобальных optimum ещё не установлено |
| `REF_PROJECTION_WIDTH` | У одного legal σ direct `W(σ)≠W(C(σ))`, например 2 и 1 | Нельзя отклонить из-за равенства корневых optimum; это refutation pathwise lemma, а последствия для optimum отдельны |
| `REF_WIDTH_VALUE_SET` | Различаются множества ширин разрезов, например `{0,1,2}` и `{0,2}`, даже при одинаковом максимуме | Неравенство максимальных ширин или optimum не требуется для этого более сильного пункта источника |
| `REF_EXPANSION_INVARIANT` | Вставка правильного числа middle copies **между собственными first/last**, полностью legal, меняет заявленный normalized side-span/width invariant | Существование другого хорошего lift ещё может сохраняться |
| `REF_EXPANSION_EXISTENCE` | Для одного legal endpoint order исчерпывающая/сертифицированная проверка **всех** full lifts исключает lift той же ширины | Ошибка одного decoder или одного chosen lift не доказывает этого |
| `REF_OPTIMUM` | Exact `OPT_full≠OPT_capped` на одном raw input, например доказанные 2 и 1 | Двух отдельных layout разной ширины недостаточно |
| `REF_DP_RECURRENCE` | Faithful frozen recurrence/transition semantics даёт результат, противоречащий независимо перечисленным endpoint orders | Bug в реализации, не следующей спецификации, остаётся software defect |
| `REF_COUNT` | Полное независимо проверенное множество legal unfiltered endpoint states/edges противоречит формуле | Пропуск ребра конкретным генератором не опровергает формулу; filtered graph не является этой целью |
| `REF_RANK_IDENTITY` | Один валидный cut имеет разные exact direct intersection dimension и independently verified rank expression | Сначала исключить field/rank software defect |

Так, pathwise контрпример **принимается против pathwise subclaim**, даже если optimum theorem на этом входе выживает. Ни `STRONG_BISIMULATION_ONLY`, ни равенство optimum не являются универсальным правилом отклонения. Каждый finding хранит `claim_id`, exact source path/predicate, target SHA, raw input и evidence hashes, theorem-domain validity, coverage class, verdict, mathematical consequence и implementation consequence.

Заранее зафиксированные **не-refutation / иные исходы**, с примерами:

- Atomic strong-bisimulation-only: `(3,1)`, `c=(1,0)` и `c'=(2,0)` имеют одинаковый q и разные next q-targets. Это диагностический finding, пока не нарушен любой из реальных пунктов выше.
- Raw continuation-only: один representative требует две оставшиеся копии, другой одну. Различие сырых suffix-языков само по себе не противоречит endpoint correspondence.
- Wrong objective: `[0,1,1,0]` и `[0,1,0]` имеют разные суммы, но одинаковые max=1.
- Wrong graph: middle-copy self-loop не обязан входить в endpoint DAG; число рёбер `width<=B` graph не сравнивается с полной формулой.
- Invalid candidate: слово `112` не является full witness для `(3,1)`; отсутствующая копия не становится математическим counterexample.
- Implementation defect: код пропустил одно legal ребро `(2,2)` или вернул malformed witness. Локализуется дефект программы; математическое утверждение требует отдельного противоречия.
- Proof gap: необходимый переход доказательства не обоснован. Это `PROOF_GAP`, а не автоматически ложность самой теоремы.
- Prior art: найден предшественник с теми же гипотезами и результатом. Это novelty finding, не ложность optimum.
- Incomplete / byte-only mismatch: timeout, недостающий лог или два разных валидных tied-optimal witnesses не устанавливают mathematical refutation.

Новое/неперечисленное правдоподобное расхождение по умолчанию — `PENDING_SOURCE_MAPPING` / `INCONCLUSIVE`, не автоматическое отклонение и не автоматическое опровержение. Сохранить allegation до исправлений. Нельзя отклонить реальный pathwise/value/count/rank falsifier, назвав его «только bisimulation». Новые правила получают prospective version с parent hash; увиденный counterexample не исключается задним числом.

**Вне кампании ≠ вне теоремы.** Например, валидный GF(5), `d=3`, `n=7` input вне зарегистрированных 1107, но может опровергать универсальную frozen A3. Он сохраняется как `EXPLORATORY_OUTSIDE_CAMPAIGN`; его нельзя отклонить только из-за K,D,F,M. Напротив, невалидное поле или нулевая кратность действительно нарушают исходный domain.

Окончательный `VALIDATED_MATHEMATICAL_REFUTATION_OF_NAMED_SUBCLAIM` требует точного source mapping, валидности raw domain, полноты нужного certificate/enumeration, отдельно написанного пересчёта, устранения software/model/objective mismatch и внешнего reviewer, независимого от авторов reference/oracle. В этой сессии возможен только `AUTHOR_REPLAYED_PENDING_EXTERNAL_ADJUDICATION`. Для graph-count или proof-gap finding поля optimum/witness/cuts допускают явное `NOT_APPLICABLE` с причиной; выдумывать числовые значения запрещено.

Adjudication: (1) закрепить allegation/raw input до исправлений; (2) проверить domain и hashes; (3) независимо пересчитать обе стороны точного alleged discrepancy: full optimum/certified bounds требуются для REF_OPTIMUM, endpoint optimum для REF_DP_RECURRENCE, а pathwise/count/rank findings — соответствующие конечные certificates; (4) проверить layout legality, все cuts, полноту перебора и целевую функцию; (5) попытаться минимизировать по фиксированному порядку `p,d,k,n,a,geometry,layout`; (6) независимо перепроверить уменьшенный input; (7) опубликовать accepted/rejected/inconclusive с причиной. Отсутствие воспроизведения из-за ошибки окружения — `INCONCLUSIVE`, не математическое отклонение.

Два layout с разной шириной не устанавливают разность **оптимумов**. Нужно точное перечисление или независимо проверяемые lower/upper certificates. Ошибку конкретной реализации не объявлять опровержением теоремы, пока не проверена сама mathematical compression/DP specification. Pathwise lemma и optimum theorem также имеют разные области refutation.

После положительного прохода формулировка только: «В полном зарегистрированном конечном наборе с указанными hash контрпример не найден». Для доказательства с неограниченными `k,d,F,a` нужна математическая аргументация, отдельно проверенная. Перечень конечных выживших тестов её не заменяет.

## 8. Выполненный dry run ложного контрпримера

**Предварительный exploratory negative control, выполненный до preregistration.** Этот пилотный запуск не засчитывается как выполнение будущей кампании 1107 confirmatory inputs и не используется для продвижения A3. Сам pilot input остаётся в полном конечном наборе §5 и при проведении кампании должен проверяться заново с раскрытием предварительного exposure. Созданный отдельно в этой сессии проверяющий не импортирует JANUS, не использует q для вычисления optimum, rank identity или endpoint transitions. Он строит spans как явные XOR-замкнутые множества векторов.

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
| **R — воспроизводимость / независимость** | `SELF_VERIFIED` → `EXTERNALLY_INSPECTED` (другой человек запускает reference) → `INDEPENDENTLY_REPLICATED` (своя реализация + raw oracle, заявленные scope/exposure) | `EXTERNAL_INDEPENDENT_REPLICATION=NOT_ESTABLISHED`. Value/count harnesses этой сессии — только `SELF_VERIFIED`, без external inspection. Cross-runner PDF PASS относится только к build |
| **N — новизна / prior art** | Declared search → `N3_NOVELTY_CANDIDATE` → external exact-equivalence/direct-subsumption review; outcomes `PRIOR_ART_SUBSUMES`, narrowed claim, либо обоснованная ограниченная novelty оценка | Источники заявляют N3; собственный новый literature audit не выполнен; `WORLD_NOVELTY_N4=NOT_ESTABLISHED` |

`EXTERNALLY_VALIDATED` без уточнения использовать нельзя: указать expert, объект, scope, report и ограничения — correctness review это или bibliographic/novelty review. Clean-room совпадение в конечном наборе устанавливает воспроизводимость на этом наборе; не доказывает универсальную lemma и не устанавливает мировой приоритет. И наоборот, prior art может лишить новизны корректную A3, не создав value counterexample.

Внешние участники работают параллельно: C атакует full semantics/proof; R пишет/запускает реализации с декларацией независимости; N ищет exact/directly subsuming результаты. Общий evidence ledger хранит hashes и отчёты, но verdict каждого трека публикуется отдельно. В рамках подготовки этого brief новые письма или приглашения не отправлялись. Отдельный публичный [SAT custodian protocol, PR #596](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/596), относится к проверке original-CNF SAT-моделей и подписанным precommit, не к A3. На прочитанном head `e3104bb94cfa92e0264ee98f486a2e3794bdaf80` [committed summary](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/e3104bb94cfa92e0264ee98f486a2e3794bdaf80/experiments/time_sat_004_external/time_sat_004d9a_evidence/summary.json) сообщает 0 approved real custodians, 0 real data sources и 0 verified external SAT models; он не повышает R/C/N статусы A3. Частная переписка по SAT-пилоту не является normative input A3 preregistration.

## 10. Pre-registration V2, crypto commitment и порядок release

Нормативный объект этой версии — **точные bytes** `A3_REFUTATION_PREREGISTRATION_V2.json` из приложения A: UTF-8 без BOM, LF, sorted keys, indent=2 и один конечный LF. SHA-256:

```text
9d8ffa4dd3ccddc5f42a2872746995d20ef96cb6a14e1adf6d00f6910cee0716
```

V2 добавляет frozen refutation/non-refutation matrix с примерами, count-пробы, правила unknown cases и раздельные specification roles. Bounds K,D,F,M и 1107 inputs не изменены. Параметры нельзя менять по результатам будущей кампании без новой prospective amendment с parent hash.

**V1 сохранена без изменения bytes:** `A3_REFUTATION_PREREGISTRATION_V1.json`, SHA-256 `93411c043dfe6058a652a0df75bff8aa3dd2216b8d5e1c5503755f30bd9729ae`, [valid protocol commit 1e663b1](https://github.com/Hawkar-usls/Janus-Fundamentum/commit/1e663b1281d148e1fdba2f6ecf91b61144efaf40). Её rejected CRLF transport attempt остаётся в прежней immutable истории и указан в V1. V2 явно ссылается на V1 и раскрывает уже виденные sources, прежний exploratory value-пилот и известные count expectations.

Порядок V2 проверяем:

1. Count-checker подготовлен и хеширован, но не запущен. Frozen source SHA-256: `60133750b000c14b8060f72c42c8b2f4237f65c6858a12933927491bde6d8607`.
2. [Commit 382cdf8](https://github.com/Hawkar-usls/Janus-Fundamentum/commit/382cdf8b62da70e95719c86982f0c94874a6b6f0) публикует V2 JSON, включая adjudication matrix, source hash и fixed count expectations. Remote bytes прочитаны обратно и совпали с локальными.
3. [Commit 1d3aecc](https://github.com/Hawkar-usls/Janus-Fundamentum/commit/1d3aeccd64bc07d85d1ac3dd9b6332fd0c07b0cc) публикует protocol digest до разрешения первого запуска. Координатор зафиксировал эту проверку в `2026-11-14T20:43:02Z`.
4. Первый count-smoke run: `2026-11-14T20:43:51.7900837Z`–`20:43:51.9104173Z`. Source hash до/после одинаков. Receipt SHA-256 `2d23df91634602cdfb38ed10292e5134c3eabf7a38f89314c4e855d528e72723`; metadata SHA-256 `d4b9668585376210b68bf697b91da335645f1365c5e4bb4b2c91476a8cdf3d00`.
5. Затем публикуется этот обновлённый brief с count source/receipt и отдельным blind raw-task contract. Полная A3-кампания не запускалась и её код не выпущен. Reference code A3 и прежний value-пилот существовали до V2; скрытой blindness авторов к ним не заявляется.

Время run metadata — запись этой сессии, а не внешняя доверенная timestamp-квитанция. Git commit связывает bytes и порядок истории, но его author/committer time сам по себе не даёт trusted time. Внешние RFC 3161/countersigned archive, независимая регистрация/acceptance и внешняя валидация **не получены**. Статус — публичный protocol commitment до нового count run и до полной кампании; первоначальный value-пилот остаётся exploratory.

Для следующих исполнителей:

1. Координатор фиксирует V2 immutable bytes/hash, выдаёт raw-oracle автору только отдельный контракт A и inputs. Для DP и proof-review применяет самостоятельные exposure-гейты §6. Общий brief не является blind packet.
2. До reference/comparison outputs фиксируются hashes реализации, environment, generator и полного input manifest. Отдельно сохраняются author/exposure declarations и наличие организационной независимости.
3. После выполнения публикуются exact coverage, actual DP state/edge sets, direct oracle answers, все findings, rejected allegations, timeouts и amendments. Новые случаи вне bounds остаются exploratory; математически валидный counterexample вне bounds не игнорируется.
4. Новый adjudication rule нельзя применить задним числом, чтобы исключить неудобный counterexample. Неперечисленный finding остаётся pending до source mapping.

Hash идентифицирует bytes, но не доказывает математическую истину, внешнюю независимость, отсутствие предварительного просмотра или мировой приоритет. `A3_REFUTATION_BRIEF.sha256` закрепляет итоговый документ отдельно, без циклического вставления собственного hash в его bytes.

## 11. Конкретное задание следующему независимому проверяющему

Координатор получает весь brief, frozen source links и preregistration hash. Raw-oracle автор получает отдельно только контракт A (приложение F / отдельный файл) и raw inputs. DP автор получает полностью определённую endpoint specification, но не reference implementation и comparison outputs до code freeze. Mathematical reviewer получает original task и проверяемое утверждение; готовый proof скрыт до фиксации собственной аргументации, если заявляется независимый вывод. Adjudicator получает необходимые evidence независимо. Все четыре роли и exposure фиксируются; один автор может выполнить инженерные проверки, но не присвоить им внешний статус.

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

В PR этой поставки добавляются документы/JSON/checksums в отдельной ветке, V1 protocol bytes сохранены, существующий brief обновлён до V2; reference algorithms, theorem/admission objects, issue #173 и Meta Registry не изменяются. PR не сливается автоматически. Коммит протокола и итоговый diff позволяют проверить изоляцию.

## 12. Что остаётся непроверенным

- Полная конечная кампания 1107 inputs и metamorphic schedule не запускалась; её outputs, candidate DP и confirmatory code ещё не созданы. Пять count-проб относятся к отдельному собственному harness; reference-DP instrumentation gate не выполнен.
- Новый универсальный математический proof review, внешний clean-room implementer и независимый adjudication реального контрпримера отсутствуют.
- Поля кроме GF(2)/GF(3), `d>2`, `k>3`, `n>6` не покрываются этим конечным протоколом; сама A3 заявляет значительно более широкую область.
- Timing, bit complexity, стоимость чтения кратностей и развёрнутого witness не следуют из счётчика `O(k*3^k)`. Этот счётчик относится к combinatorial DP после rank preprocessing. Чтение входа/полевые операции учитываются отдельно; выдача полного layout требует как минимум `Ω(n)` вывода.
- Производительность новых реализаций, расширенные field libraries, полный replay CI/PDF, cross-environment build и новая мировая literature novelty не проверены.
- Value-пилот подтверждает работу отрицательного контроля на одном входе. Пять count-проб проверяют literal graph-harness на пяти профилях; оба результата только SELF_VERIFIED. Их создание разными агентами одной сессии не даёт внешней независимости.

Потолки сохраняются: `EXTERNAL_INDEPENDENT_REPLICATION=NOT_ESTABLISHED`, `WORLD_NOVELTY_N4=NOT_ESTABLISHED`, `P_VS_NP=OPEN`. Достижение этой поставки — проверяемый протокол и отрицательный контроль с источниками, границами и правилом честного verdict.


## Приложение A. Нормативная preregistration V2

Exact UTF-8 LF bytes; один конечный LF перед закрывающей оградой. V1 сохранена отдельно.

```json
{
  "amendment": {
    "bounds_changed": false,
    "date_local": "2026-11-14",
    "exposure": "Authors saw A3 sources, previous brief and exploratory value-pilot output. Five count expectations are known constants. New count source is prepared and hashed but NOT RUN at registration. No full campaign has run.",
    "old_bytes_preserved": true,
    "parent_protocol_commit": "1e663b1281d148e1fdba2f6ecf91b61144efaf40",
    "parent_sha256": "93411c043dfe6058a652a0df75bff8aa3dd2216b8d5e1c5503755f30bd9729ae",
    "prior_brief_head": "5cf85e8258e6412a0d78cd777cf98b71b08a10b0",
    "reason": "Before the 1107-input campaign, freeze explicit subclaim refutation/non-refutation rules with examples; add literal DAG count probes; separate blinded raw-oracle, algorithm-reimplementation and proof-review roles."
  },
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
  "candidate_acceptance": "Use the frozen refutation_policy. One discrepancy opens a candidate; mathematical refutation, software defect and proof gap are distinct verdicts with exact target and independence limits.",
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
  "count_smoke": {
    "controls": [
      "remove_one_legal_edge",
      "add_illegal_sink_to_source_edge",
      "alter_predicted_vertex_count"
    ],
    "observed_method": "Enumerate literal singleton atom / repeated start-finish states and unique directed edges; do not derive observed counts from formula. Serialize every vertex/edge and forward/reverse BFS sets. Counts concern the unfiltered admissible DAG.",
    "pass_rule": "All five observed vertex/edge counts match fixed constants, all unrestricted vertices reachable and co-reachable, and all 15 tamper controls reject.",
    "probes": [
      {
        "a": [
          3,
          1
        ],
        "edges": 7,
        "r": 1,
        "s": 1,
        "states": 6
      },
      {
        "a": [
          2,
          1
        ],
        "edges": 7,
        "r": 1,
        "s": 1,
        "states": 6
      },
      {
        "a": [
          2,
          2
        ],
        "edges": 12,
        "r": 2,
        "s": 0,
        "states": 9
      },
      {
        "a": [
          1,
          1
        ],
        "edges": 4,
        "r": 0,
        "s": 2,
        "states": 4
      },
      {
        "a": [
          1,
          1,
          1
        ],
        "edges": 12,
        "r": 0,
        "s": 3,
        "states": 8
      }
    ],
    "reference_dp_instrumentation_gate": "Future independent/reference DP must expose its actual allocated/admissible/reachable states and executed legal transition set. Compare sets and unique counts with literal checker for each fixed probe and every scheduled campaign input. This standalone smoke checker does not itself run or validate the reference DP.",
    "run_order": "Commit and read back this V2 registration and its digest before first count-smoke execution and before code/receipt release.",
    "scientific_status_ceiling": "Only after a successful run: at most AUTHOR_SESSION_SELF_VERIFIED_HARNESS_QUALITY_ONLY; not external inspection, replication or general formula proof.",
    "separate_from_value_pilot": true,
    "source_sha256": "60133750b000c14b8060f72c42c8b2f4237f65c6858a12933927491bde6d8607",
    "status_at_freeze": "SOURCE_HASHED_NOT_EXECUTED"
  },
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
  "protocol_id": "A3_REFUTATION_BRIEF_V2",
  "randomness": "NONE_IN_CONFIRMATORY_CAMPAIGN",
  "receipt_not_applicable_rule": "For graph-count, proof-gap or other non-value findings, optimum/witness/cut fields may be explicit NOT_APPLICABLE with reason; never invent numeric values to satisfy the receipt schema.",
  "refutation_policy": {
    "adjudication_states": [
      "CANDIDATE_PENDING",
      "AUTHOR_REPLAYED_PENDING_EXTERNAL_ADJUDICATION",
      "VALIDATED_MATHEMATICAL_REFUTATION_OF_NAMED_SUBCLAIM",
      "IMPLEMENTATION_DEFECT",
      "PROOF_GAP",
      "NON_REFUTATION_DIAGNOSTIC",
      "REJECTED_INVALID_CANDIDATE",
      "INCONCLUSIVE"
    ],
    "candidate_threshold": 1,
    "frozen_before_campaign": true,
    "mathematical_refutations": [
      {
        "consequence": "Refutes this pathwise subclaim; optimum consequence separately UNDETERMINED.",
        "example": "Hypothetical: a legal sigma has a normalized support pair absent from its computed C(sigma). Supply both traces, class spans and exact input; no actual such example is claimed.",
        "falsifier": "One valid full layout with a different normalized support-pair trace after exact first/last deletion.",
        "id": "REF_SUPPORT_TRACE",
        "predicate": "For any legal full layout, deletion of middle occurrences preserves its ordered cut support-pair trace up to consecutive duplicates.",
        "target": "Compression theorem fixed_order/compression_statement"
      },
      {
        "consequence": "Pathwise lemma refuted; optimum theorem assessed separately.",
        "example": "Hypothetical direct W(sigma)=2,W(C(sigma))=1, each exact cut checked. This refutes pathwise preservation even if both global optima coincide.",
        "falsifier": "One legal full layout and its prescribed compression with unequal direct maximum cut widths.",
        "id": "REF_PROJECTION_WIDTH",
        "predicate": "W(C(sigma))=W(sigma) for every legal full layout.",
        "target": "Compression proof pathwise width preservation"
      },
      {
        "consequence": "This pathwise subclaim refuted; optimum consequence assessed separately.",
        "example": "Hypothetical full cut-value set {0,1,2} versus compressed {0,2}; equal maxima do not rescue the named set-preservation claim.",
        "falsifier": "One valid full layout and its prescribed compression with unequal independently checked cut-width value sets, even if maxima agree.",
        "id": "REF_WIDTH_VALUE_SET",
        "predicate": "The set of cut-width values of a legal full layout equals that of its exact first/last compression.",
        "target": "Compression theorem compression_statement cut-width value-set preservation"
      },
      {
        "consequence": "Named pathwise expansion invariant refuted; expansion existence and optimum adjudicated separately.",
        "example": "Hypothetical legal between-endpoint insertion changes a side-span pair or width set. This refutes that invariant even if another lift still attains equal width.",
        "falsifier": "One legal source-conforming insertion with a directly verified failure of the named span/width invariant; validate endpoint order, copy counts and between-endpoint positions first.",
        "id": "REF_EXPANSION_INVARIANT",
        "predicate": "Inserting only the required middle copies strictly between their own first and last endpoints preserves normalized side-span trace and cut-width values.",
        "target": "Compression proof middle-copy insertion invariant"
      },
      {
        "consequence": "Expansion-existence subclaim refuted.",
        "example": "Hypothetical endpoint width 1 while every full lift has width at least 2. Failure of one chosen decoder alone is insufficient.",
        "falsifier": "One endpoint order for which exhaustive/certified search of all legal lifts proves none has equal width.",
        "id": "REF_EXPANSION_EXISTENCE",
        "predicate": "Every legal endpoint order has a full legal lift at the prescribed multiplicities with the same width.",
        "target": "Compression proof converse expansion"
      },
      {
        "consequence": "Optimum-compression subclaim refuted.",
        "example": "Hypothetical certified minima 2 versus 1. Two layouts of widths 2 and 1 do not suffice.",
        "falsifier": "Different exact minima on the same valid raw geometry, with complete enumerations or independently checked upper/lower certificates.",
        "id": "REF_OPTIMUM",
        "predicate": "OPT_full(U,a)=OPT_capped(U,min(a,2)).",
        "target": "A3 exact optimum preservation"
      },
      {
        "consequence": "Frozen algorithmic subclaim refuted; a bug in a non-faithful implementation is not enough.",
        "example": "Hypothetical faithfully evaluated frozen recurrence returns 2 while exhaustive legal endpoint orders attain minimum 1.",
        "falsifier": "Mismatch after validating faithful recurrence/transitions and independently enumerating endpoint layouts.",
        "id": "REF_DP_RECURRENCE",
        "predicate": "The exact frozen recurrence over the specified legal DAG returns the minimum endpoint-layout bottleneck width.",
        "target": "Published endpoint-DP correctness"
      },
      {
        "consequence": "Exact counting subclaim refuted; optimum consequence separately UNDETERMINED.",
        "example": "Hypothetical complete graph for (2,2) has 9 states and 11 legal edges rather than 12; showing a buggy generator omitted an edge only refutes that generator.",
        "falsifier": "A complete, independently verified legal vertex/edge set at a valid multiplicity profile has a different count.",
        "id": "REF_COUNT",
        "predicate": "Unique states and legal directed edges equal the stated mixed-state formulas.",
        "target": "Exact unfiltered admissible endpoint-DAG state/edge counts"
      },
      {
        "consequence": "Width-identity subclaim refuted.",
        "example": "Hypothetical direct intersection dimension 1 while verified ranks yield 2; field/arithmetic defects eliminated first.",
        "falsifier": "Valid finite-field geometry/cut with exact independently checked unequal sides.",
        "id": "REF_RANK_IDENTITY",
        "predicate": "Direct dim(L intersect R)=rho(S)+rho(I minus P)-rho(I) at every admissible cut.",
        "target": "State width rank identity"
      }
    ],
    "no_posthoc_escape": "A mismatch may not be rejected solely by calling it bisimulation-only if it also satisfies any named pathwise, optimum, expansion, rank or count falsifier. Preserve all allegations and reasons. New decision rules require a prospectively hashed amendment; never retroactively exclude an observed counterexample.",
    "non_refutations": [
      {
        "example": "a=(3,1),c=(1,0),c_prime=(2,0): same endpoint Active/NotStarted; next class-1 target Active versus Done.",
        "id": "DIAG_STRONG_BISIMULATION",
        "rule": "Exact atomic strong bisimulation failure alone is diagnostic, not A3 refutation."
      },
      {
        "example": "One representative needs two remaining class-1 occurrences and another needs one; compare normalized endpoint traces separately.",
        "id": "DIAG_RAW_CONTINUATION",
        "rule": "Different raw suffix word lengths/multiplicities alone are diagnostic."
      },
      {
        "example": "For one repeated line, cut arrays [0,1,1,0] and [0,1,0] have different sums but equal maxima 1.",
        "id": "WRONG_OBJECTIVE",
        "rule": "Additive sums, trace lengths or number of cuts do not replace min-max width."
      },
      {
        "example": "A missing middle-copy self-loop, or fewer edges after filtering by width<=B, does not contradict the unfiltered DAG count formula.",
        "id": "WRONG_GRAPH",
        "rule": "Original occurrence edges, q-stuttering loops and width-filtered graphs are not the complete unfiltered endpoint DAG."
      },
      {
        "example": "Word 112 is not a full layout for multiplicities (3,1).",
        "id": "INVALID_LAYOUT",
        "rule": "Missing/extra copies or illegal precedence are rejected as candidate evidence."
      },
      {
        "example": "A generator that deletes one legal edge for (2,2) yields 11; repairing that omission removes the discrepancy.",
        "id": "IMPLEMENTATION_ONLY",
        "rule": "Unfaithful transitions, bad arithmetic or a broken witness decoder are software defects until linked to a frozen mathematical subclaim."
      },
      {
        "example": "An argument assumes an unsupported equivalence; report the exact gap and independent status, without inventing a counterexample.",
        "id": "PROOF_GAP_ONLY",
        "rule": "An unproved inference may invalidate a proof route without proving the theorem false."
      },
      {
        "example": "An earlier equivalent exact algorithm is found and mapped to the same hypotheses.",
        "id": "PRIOR_ART_ONLY",
        "rule": "A directly subsuming theorem concerns novelty and does not by itself disprove values."
      },
      {
        "example": "Different tied optimal words both validate at width 1; byte mismatch alone is irrelevant to optimum.",
        "id": "INCOMPLETE_OR_NUMERIC_ONLY",
        "rule": "Timeouts, missing coverage, hash mismatches or differing valid optimal witnesses do not establish mathematical refutation."
      }
    ],
    "scope_rule": "Separate OUTSIDE_CAMPAIGN_BOUNDS from OUTSIDE_THEOREM_DOMAIN. A valid exploratory counterexample beyond K,D,F,M may refute the universal frozen target, but is not confirmatory coverage of the 1107 set.",
    "unlisted_case_default": "PENDING_SOURCE_MAPPING; never automatic rejection merely because unlisted, never automatic theorem refutation.",
    "validation_gate": "Name exact target proposition/SHA, validate raw domain and completeness, replay with a separately authored method, eliminate implementation/model/objective mismatch, publish evidence and exposure. Final external validation requires a reviewer genuinely independent of the original/reference and oracle authors. Same-session checks remain SELF_VERIFIED and pending that gate."
  },
  "registration_revision": "2.0.0",
  "release_order": [
    "Preserve V1 immutable bytes; publish V2 amendment with parent hash and all verdict/count/spec-role rules before campaign or count-smoke run.",
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
    "all_cut_widths",
    "claim_id",
    "target_source_path_and_predicate",
    "theorem_domain_validity",
    "campaign_coverage_class",
    "adjudication_verdict",
    "mathematical_consequence",
    "implementation_consequence",
    "evidence_and_checker_hashes",
    "independence_and_exposure_limits"
  ],
  "schema": "janus.a3.refutation.preregistration.v2",
  "specification_roles": {
    "adjudicator": "Separate independent human/expert and exact checker; same-session authors cannot self-assign external status.",
    "dp_packet": "Complete frozen theorem and transition specification, but no reference code or answers before freeze. Tests independent algorithm implementation, not independent discovery of lemma.",
    "not_underdetermined": "Original optimization task is fully determined. Independence from compression is achieved by excluding it from raw-oracle assumptions, not by omitting necessary problem definitions.",
    "proof_review_packet": "Original task plus explicitly named compression claim; reviewer derives a valid argument or counterexample. For independent derivation withhold frozen proof text until reviewer freezes argument/exposure declaration.",
    "raw_oracle_packet": {
      "contains": "Fully specified original task only, no q/compression lemma/endpoint recurrence/formula/expected outputs. No duty to derive compression.",
      "file": "A3_RAW_ORACLE_CONTRACT_V2.md",
      "sha256": "9b56d11d01a5dc02e819d24b480f3cca395e5ed6a87ad2bc72924510da634a72"
    }
  },
  "stop_rule": "Preserve the first discrepancy and minimal reproduction immediately; continue in-domain cases if budget permits. A complete no-refutation report requires every scheduled check completed and adjudicated, not equality in stronger-property diagnostics; a validated refutation needs one case.",
  "study_status_at_freeze": "NOT_STARTED",
  "target_publication_sha": "811d954e52296893898062d9abea7aaf572629be",
  "timezone": "Europe/Kiev"
}
```


## Приложение B. Первоначальный exploratory value-checker

Сохранить как reject_false_counterexample.py, UTF-8 LF, один конечный LF. Выполнить python reject_false_counterexample.py.

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


## Приложение C. Первоначальный value-pilot receipt

Читаемое JSON с LF. Для исходного Windows byte hash восстановить CRLF и конечный CRLF.

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


## Приложение D. Frozen count-checker V2

Сохранить как endpoint_count_smoke.py, UTF-8 LF и один конечный LF. Выполнить python endpoint_count_smoke.py. Source hash совпадает с frozen V2. Это собственный harness, не reference DP.

```python
"""Fixed endpoint-DAG COUNT probes; do not mistake this for an A3 proof.

The observed graph is enumerated literally by atom/start/finish events.
No count formula or JANUS code is used. This author-session harness is not
an independent reference DP and cannot establish external validation.

Preparation rule: do not execute before the V2 preregistration is committed.
"""

from collections import deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


# Frozen expected constants, separate from the observed graph construction.
PROBES = (
    {"id": "m3_1", "multiplicities": (3, 1), "expected_vertices": 6, "expected_edges": 7},
    {"id": "m2_1", "multiplicities": (2, 1), "expected_vertices": 6, "expected_edges": 7},
    {"id": "m2_2", "multiplicities": (2, 2), "expected_vertices": 9, "expected_edges": 12},
    {"id": "m1_1", "multiplicities": (1, 1), "expected_vertices": 4, "expected_edges": 4},
    {"id": "m1_1_1", "multiplicities": (1, 1, 1), "expected_vertices": 8, "expected_edges": 12},
)


def literal_admissible_graph(multiplicities):
    """0=NotStarted, 1=Active, 2=Done; singleton has no Active state."""
    if any(type(m) is not int or m < 1 for m in multiplicities):
        raise ValueError("positive integer multiplicities required")
    alphabets = [(0, 2) if m == 1 else (0, 1, 2) for m in multiplicities]
    vertices = set(product(*alphabets))
    edges = set()
    for state in sorted(vertices):
        for j, m in enumerate(multiplicities):
            successor = list(state)
            if m == 1:
                if state[j] != 0:
                    continue
                successor[j] = 2  # singleton atom
            else:
                if state[j] == 0:
                    successor[j] = 1  # first occurrence: start
                elif state[j] == 1:
                    successor[j] = 2  # last occurrence: finish
                else:
                    continue
            successor = tuple(successor)
            if successor not in vertices:
                raise AssertionError("transition leaves admissible domain")
            edges.add((state, successor))
    return vertices, edges


def bfs(start, vertices, edges, reverse=False):
    adjacency = {vertex: [] for vertex in vertices}
    for u, v in edges:
        if u not in vertices or v not in vertices:
            raise ValueError("edge endpoint outside vertex set")
        adjacency[v if reverse else u].append(u if reverse else v)
    visited = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for successor in adjacency[vertex]:
            if successor not in visited:
                visited.add(successor)
                queue.append(successor)
    return visited


def graph_record(scope, vertices, edges):
    return {
        "scope": scope,
        "observed_unique_vertex_count": len(vertices),
        "observed_unique_directed_edge_count": len(edges),
        "vertices": [list(v) for v in sorted(vertices)],
        "unique_directed_edges": [[list(u), list(v)] for u, v in sorted(edges)],
    }


def verify_candidate(candidate_vertices, candidate_edges, claimed_counts,
                     expected_vertices, expected_edges):
    """Exact set comparison plus separately supplied count assertions."""
    failures = []
    if candidate_vertices != expected_vertices:
        failures.append("vertex_set_mismatch")
    if candidate_edges != expected_edges:
        failures.append("edge_set_mismatch")
    observed_counts = (len(candidate_vertices), len(candidate_edges))
    if observed_counts != claimed_counts:
        failures.append("predicted_count_mismatch")
    return {"verdict": "REJECTED" if failures else "ACCEPTED", "failures": failures}


def run_probe(probe):
    multiplicities = probe["multiplicities"]
    vertices, edges = literal_admissible_graph(multiplicities)
    predicted_counts = (probe["expected_vertices"], probe["expected_edges"])
    source = (0,) * len(multiplicities)
    sink = (2,) * len(multiplicities)
    reachable = bfs(source, vertices, edges)
    coreachable = bfs(sink, vertices, edges, reverse=True)
    filtered_vertices = reachable & coreachable
    filtered_edges = {(u, v) for u, v in edges
                      if u in filtered_vertices and v in filtered_vertices}

    baseline = verify_candidate(vertices, edges, predicted_counts, vertices, edges)
    filtered_check = verify_candidate(filtered_vertices, filtered_edges,
                                      predicted_counts, vertices, edges)
    # Controls change candidate records only; the literal reference is unchanged.
    first_edge = min(edges)
    missing_edges = set(edges)
    missing_edges.remove(first_edge)
    extra_edge = (sink, source)  # backward edge forbidden by endpoint events
    if extra_edge in edges:
        raise AssertionError("extra-edge control was not extra")
    extra_edges = edges | {extra_edge}
    controls = [
        {"case": "missing_edge", "mutation": [[list(v) for v in first_edge]],
         **verify_candidate(vertices, missing_edges, predicted_counts, vertices, edges)},
        {"case": "extra_edge", "mutation": [[list(v) for v in extra_edge]],
         **verify_candidate(vertices, extra_edges, predicted_counts, vertices, edges)},
        {"case": "wrong_predicted_count",
         "mutated_prediction": [predicted_counts[0] + 1, predicted_counts[1]],
         **verify_candidate(vertices, edges, (predicted_counts[0] + 1, predicted_counts[1]),
                            vertices, edges)},
    ]
    if baseline["verdict"] != "ACCEPTED" or filtered_check["verdict"] != "ACCEPTED":
        raise AssertionError("fixed count probe or reachability check failed")
    if any(control["verdict"] != "REJECTED" for control in controls):
        raise AssertionError("tamper control failed open")
    return {
        "probe_id": probe["id"],
        "multiplicities": list(multiplicities),
        "fixed_expected_unique_counts": list(predicted_counts),
        "full_admissible_graph": graph_record("full_admissible_endpoint_graph", vertices, edges),
        "reachable_vertices": [list(v) for v in sorted(reachable)],
        "coreachable_vertices": [list(v) for v in sorted(coreachable)],
        "filtered_graph": graph_record("reachable_coreachable_induced_graph",
                                       filtered_vertices, filtered_edges),
        "full_vs_filtered_equal": vertices == filtered_vertices and edges == filtered_edges,
        "baseline_count_check": baseline,
        "filtered_count_check": filtered_check,
        "tamper_controls": controls,
    }


def main():
    source_path = Path(__file__)
    probes = [run_probe(probe) for probe in PROBES]
    receipt = {
        "schema": "a3.endpoint_dag_count_smoke.v2",
        "source_sha256": sha256(source_path.read_bytes()).hexdigest(),
        "scope": "Only five fixed endpoint-DAG COUNT probes; no full 1107-case campaign.",
        "status_track": "AUTHOR_SESSION_SELF_VERIFIED_HARNESS_QUALITY_ONLY",
        "limits": [
            "No reference-DP execution or output comparison.",
            "No external or clean-room scientific validation.",
            "No proof of the general count formula or A3 endpoint compression.",
            "Full admissible and reachable/coreachable graphs are reported separately.",
        ],
        "probes": probes,
        "verdict": "ALL_FIXED_COUNT_PROBES_AND_TAMPER_CONTROLS_PASSED",
    }
    destination = source_path.with_name("count_smoke_receipt.json")
    destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"verdict": receipt["verdict"], "probe_count": len(probes),
                      "source_sha256": receipt["source_sha256"],
                      "receipt_sha256": sha256(destination.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
```


## Приложение E. Полный count receipt и run metadata

Первый compact JSON содержит все вершины/рёбра и tamper verdicts. Для восстановления первоначального receipt: json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True)+конечный LF, затем LF→CRLF. SHA-256 исходных bytes: 2d23df91634602cdfb38ed10292e5134c3eabf7a38f89314c4e855d528e72723. В replay ZIP сохранены исходные bytes.

```json
{"limits":["No reference-DP execution or output comparison.","No external or clean-room scientific validation.","No proof of the general count formula or A3 endpoint compression.","Full admissible and reachable/coreachable graphs are reported separately."],"probes":[{"baseline_count_check":{"failures":[],"verdict":"ACCEPTED"},"coreachable_vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]],"filtered_count_check":{"failures":[],"verdict":"ACCEPTED"},"filtered_graph":{"observed_unique_directed_edge_count":7,"observed_unique_vertex_count":6,"scope":"reachable_coreachable_induced_graph","unique_directed_edges":[[[0,0],[0,2]],[[0,0],[1,0]],[[0,2],[1,2]],[[1,0],[1,2]],[[1,0],[2,0]],[[1,2],[2,2]],[[2,0],[2,2]]],"vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]]},"fixed_expected_unique_counts":[6,7],"full_admissible_graph":{"observed_unique_directed_edge_count":7,"observed_unique_vertex_count":6,"scope":"full_admissible_endpoint_graph","unique_directed_edges":[[[0,0],[0,2]],[[0,0],[1,0]],[[0,2],[1,2]],[[1,0],[1,2]],[[1,0],[2,0]],[[1,2],[2,2]],[[2,0],[2,2]]],"vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]]},"full_vs_filtered_equal":true,"multiplicities":[3,1],"probe_id":"m3_1","reachable_vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]],"tamper_controls":[{"case":"missing_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[0,0],[0,2]]],"verdict":"REJECTED"},{"case":"extra_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[2,2],[0,0]]],"verdict":"REJECTED"},{"case":"wrong_predicted_count","failures":["predicted_count_mismatch"],"mutated_prediction":[7,7],"verdict":"REJECTED"}]},{"baseline_count_check":{"failures":[],"verdict":"ACCEPTED"},"coreachable_vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]],"filtered_count_check":{"failures":[],"verdict":"ACCEPTED"},"filtered_graph":{"observed_unique_directed_edge_count":7,"observed_unique_vertex_count":6,"scope":"reachable_coreachable_induced_graph","unique_directed_edges":[[[0,0],[0,2]],[[0,0],[1,0]],[[0,2],[1,2]],[[1,0],[1,2]],[[1,0],[2,0]],[[1,2],[2,2]],[[2,0],[2,2]]],"vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]]},"fixed_expected_unique_counts":[6,7],"full_admissible_graph":{"observed_unique_directed_edge_count":7,"observed_unique_vertex_count":6,"scope":"full_admissible_endpoint_graph","unique_directed_edges":[[[0,0],[0,2]],[[0,0],[1,0]],[[0,2],[1,2]],[[1,0],[1,2]],[[1,0],[2,0]],[[1,2],[2,2]],[[2,0],[2,2]]],"vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]]},"full_vs_filtered_equal":true,"multiplicities":[2,1],"probe_id":"m2_1","reachable_vertices":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]],"tamper_controls":[{"case":"missing_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[0,0],[0,2]]],"verdict":"REJECTED"},{"case":"extra_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[2,2],[0,0]]],"verdict":"REJECTED"},{"case":"wrong_predicted_count","failures":["predicted_count_mismatch"],"mutated_prediction":[7,7],"verdict":"REJECTED"}]},{"baseline_count_check":{"failures":[],"verdict":"ACCEPTED"},"coreachable_vertices":[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]],"filtered_count_check":{"failures":[],"verdict":"ACCEPTED"},"filtered_graph":{"observed_unique_directed_edge_count":12,"observed_unique_vertex_count":9,"scope":"reachable_coreachable_induced_graph","unique_directed_edges":[[[0,0],[0,1]],[[0,0],[1,0]],[[0,1],[0,2]],[[0,1],[1,1]],[[0,2],[1,2]],[[1,0],[1,1]],[[1,0],[2,0]],[[1,1],[1,2]],[[1,1],[2,1]],[[1,2],[2,2]],[[2,0],[2,1]],[[2,1],[2,2]]],"vertices":[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]},"fixed_expected_unique_counts":[9,12],"full_admissible_graph":{"observed_unique_directed_edge_count":12,"observed_unique_vertex_count":9,"scope":"full_admissible_endpoint_graph","unique_directed_edges":[[[0,0],[0,1]],[[0,0],[1,0]],[[0,1],[0,2]],[[0,1],[1,1]],[[0,2],[1,2]],[[1,0],[1,1]],[[1,0],[2,0]],[[1,1],[1,2]],[[1,1],[2,1]],[[1,2],[2,2]],[[2,0],[2,1]],[[2,1],[2,2]]],"vertices":[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]},"full_vs_filtered_equal":true,"multiplicities":[2,2],"probe_id":"m2_2","reachable_vertices":[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]],"tamper_controls":[{"case":"missing_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[0,0],[0,1]]],"verdict":"REJECTED"},{"case":"extra_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[2,2],[0,0]]],"verdict":"REJECTED"},{"case":"wrong_predicted_count","failures":["predicted_count_mismatch"],"mutated_prediction":[10,12],"verdict":"REJECTED"}]},{"baseline_count_check":{"failures":[],"verdict":"ACCEPTED"},"coreachable_vertices":[[0,0],[0,2],[2,0],[2,2]],"filtered_count_check":{"failures":[],"verdict":"ACCEPTED"},"filtered_graph":{"observed_unique_directed_edge_count":4,"observed_unique_vertex_count":4,"scope":"reachable_coreachable_induced_graph","unique_directed_edges":[[[0,0],[0,2]],[[0,0],[2,0]],[[0,2],[2,2]],[[2,0],[2,2]]],"vertices":[[0,0],[0,2],[2,0],[2,2]]},"fixed_expected_unique_counts":[4,4],"full_admissible_graph":{"observed_unique_directed_edge_count":4,"observed_unique_vertex_count":4,"scope":"full_admissible_endpoint_graph","unique_directed_edges":[[[0,0],[0,2]],[[0,0],[2,0]],[[0,2],[2,2]],[[2,0],[2,2]]],"vertices":[[0,0],[0,2],[2,0],[2,2]]},"full_vs_filtered_equal":true,"multiplicities":[1,1],"probe_id":"m1_1","reachable_vertices":[[0,0],[0,2],[2,0],[2,2]],"tamper_controls":[{"case":"missing_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[0,0],[0,2]]],"verdict":"REJECTED"},{"case":"extra_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[2,2],[0,0]]],"verdict":"REJECTED"},{"case":"wrong_predicted_count","failures":["predicted_count_mismatch"],"mutated_prediction":[5,4],"verdict":"REJECTED"}]},{"baseline_count_check":{"failures":[],"verdict":"ACCEPTED"},"coreachable_vertices":[[0,0,0],[0,0,2],[0,2,0],[0,2,2],[2,0,0],[2,0,2],[2,2,0],[2,2,2]],"filtered_count_check":{"failures":[],"verdict":"ACCEPTED"},"filtered_graph":{"observed_unique_directed_edge_count":12,"observed_unique_vertex_count":8,"scope":"reachable_coreachable_induced_graph","unique_directed_edges":[[[0,0,0],[0,0,2]],[[0,0,0],[0,2,0]],[[0,0,0],[2,0,0]],[[0,0,2],[0,2,2]],[[0,0,2],[2,0,2]],[[0,2,0],[0,2,2]],[[0,2,0],[2,2,0]],[[0,2,2],[2,2,2]],[[2,0,0],[2,0,2]],[[2,0,0],[2,2,0]],[[2,0,2],[2,2,2]],[[2,2,0],[2,2,2]]],"vertices":[[0,0,0],[0,0,2],[0,2,0],[0,2,2],[2,0,0],[2,0,2],[2,2,0],[2,2,2]]},"fixed_expected_unique_counts":[8,12],"full_admissible_graph":{"observed_unique_directed_edge_count":12,"observed_unique_vertex_count":8,"scope":"full_admissible_endpoint_graph","unique_directed_edges":[[[0,0,0],[0,0,2]],[[0,0,0],[0,2,0]],[[0,0,0],[2,0,0]],[[0,0,2],[0,2,2]],[[0,0,2],[2,0,2]],[[0,2,0],[0,2,2]],[[0,2,0],[2,2,0]],[[0,2,2],[2,2,2]],[[2,0,0],[2,0,2]],[[2,0,0],[2,2,0]],[[2,0,2],[2,2,2]],[[2,2,0],[2,2,2]]],"vertices":[[0,0,0],[0,0,2],[0,2,0],[0,2,2],[2,0,0],[2,0,2],[2,2,0],[2,2,2]]},"full_vs_filtered_equal":true,"multiplicities":[1,1,1],"probe_id":"m1_1_1","reachable_vertices":[[0,0,0],[0,0,2],[0,2,0],[0,2,2],[2,0,0],[2,0,2],[2,2,0],[2,2,2]],"tamper_controls":[{"case":"missing_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[0,0,0],[0,0,2]]],"verdict":"REJECTED"},{"case":"extra_edge","failures":["edge_set_mismatch","predicted_count_mismatch"],"mutation":[[[2,2,2],[0,0,0]]],"verdict":"REJECTED"},{"case":"wrong_predicted_count","failures":["predicted_count_mismatch"],"mutated_prediction":[9,12],"verdict":"REJECTED"}]}],"schema":"a3.endpoint_dag_count_smoke.v2","scope":"Only five fixed endpoint-DAG COUNT probes; no full 1107-case campaign.","source_sha256":"60133750b000c14b8060f72c42c8b2f4237f65c6858a12933927491bde6d8607","status_track":"AUTHOR_SESSION_SELF_VERIFIED_HARNESS_QUALITY_ONLY","verdict":"ALL_FIXED_COUNT_PROBES_AND_TAMPER_CONTROLS_PASSED"}
```

Run metadata (readable JSON; исходный byte hash относится к файлу в ZIP):

```json
{
  "schema": "a3.endpoint_count_run_metadata.v2",
  "status": "AUTHOR_SELF",
  "scope": "Five fixed endpoint-DAG COUNT smoke probes only; no 1107 campaign, no reference DP, no external validation",
  "started_utc": "2026-11-14T20:43:51.7900837Z",
  "ended_utc": "2026-11-14T20:43:51.9104173Z",
  "source_sha256_before": "60133750b000c14b8060f72c42c8b2f4237f65c6858a12933927491bde6d8607",
  "source_sha256_after": "60133750b000c14b8060f72c42c8b2f4237f65c6858a12933927491bde6d8607",
  "protocol_sha256": "9d8ffa4dd3ccddc5f42a2872746995d20ef96cb6a14e1adf6d00f6910cee0716",
  "receipt_sha256": "2d23df91634602cdfb38ed10292e5134c3eabf7a38f89314c4e855d528e72723",
  "prereg_commit_reported_by_coordinator": "382cdf8b62da70e95719c86982f0c94874a6b6f0",
  "prereg_digest_commit_reported_by_coordinator": "1d3aeccd64bc07d85d1ac3dd9b6332fd0c07b0cc",
  "prereg_digest_utc_reported_by_coordinator": "2026-11-14T20:43:02Z",
  "environment": {
    "python_version": "3.14.2 (tags/v3.14.2:df79316, Dec  5 2025, 17:18:21) [MSC v.1944 64 bit (AMD64)]",
    "python_executable": "C:\\Users\\hawka\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
    "platform": "Windows-10-10.0.19045-SP0",
    "architecture": "AMD64"
  },
  "powershell_version": "7.6.9",
  "exit_code": 0,
  "checker_stdout": "{\"probe_count\": 5, \"receipt_sha256\": \"2d23df91634602cdfb38ed10292e5134c3eabf7a38f89314c4e855d528e72723\", \"source_sha256\": \"60133750b000c14b8060f72c42c8b2f4237f65c6858a12933927491bde6d8607\", \"verdict\": \"ALL_FIXED_COUNT_PROBES_AND_TAMPER_CONTROLS_PASSED\"}"
}
```


## Приложение F. Отдельный пакет raw-oracle автора

Содержимое этого Markdown-блока совпадает с A3_RAW_ORACLE_CONTRACT_V2.md. Координатор передаёт только этот пакет и inputs. Весь brief не является blind packet.

```markdown
# Контракт независимого точного oracle: исходная задача об occurrence-порядках

Этот пакет полностью задаёт исходную конечную задачу. Он не предполагает никакого правила сжатия. Исполнитель получает только этот контракт и raw inputs. До фиксации своей реализации он не получает reference implementation, candidate algorithm, proof, контрольные ответы или результаты сравнений. Свою фактическую осведомлённость исполнитель декларирует отдельно; название пакета само по себе не обеспечивает blindness.

## Вход

UTF-8 JSON: `p,d,classes:[{id,basis}],multiplicities`.

- `p` — простое число; поле состоит из вычетов по модулю p.
- `d` — неотрицательная ambient dimension.
- `basis` — список векторов длины d с координатами 0..p-1. Пустой список задаёт нулевое подпространство.
- Каждая class задаёт линейную оболочку своих векторов. Геометрические подпространства классов попарно различны, независимо от различий в их списках векторов.
- `multiplicities[j]=a_j` — положительное целое число копий соответствующего класса.
- Кампания генератора ограничена p∈{2,3}, d≤2, числом классов≤3, суммой кратностей≤6. Вход за этими границами — отдельный exploratory request, а не автоматически математически некорректный вход.

## Допустимые решения и цель

Допустимый layout — слово σ из class IDs, содержащее ровно a_j копий каждого класса, без дополнительных ограничений порядка.

На каждом cut i от 0 до n=sum(a_j), включая обе границы, L_i — линейная оболочка векторов классов в префиксе σ[0:i], R_i — линейная оболочка векторов классов в суффиксе σ[i:n]. Ширина cut равна dim(L_i∩R_i). Ширина layout — максимум этих ширин. Требуется минимальная ширина среди всех допустимых layout и хотя бы один layout, достигающий минимума.

## Полный метод проверки

Перечислить все class-слова с указанными исходными кратностями. Их должно быть n!/prod(a_j!). На каждом cut получить L_i и R_i как явные множества векторов, используя линейные комбинации в GF(p). Пересечь множества. Размерность получить как единственное целое r с |L_i∩R_i|=p^r; не использовать floating logarithm. После максимума по cuts взять минимум по всем словам.

Oracle не импортирует код кандидата или JANUS, не использует преобразование задачи, endpoint events, факторизацию состояний, формулу через subset ranks или контрольные значения optimum. Все эти сведения находятся за гейтом exposure. Координатор обязан передавать этот контракт отдельно от общего исследовательского brief.

## Выход и freeze

На каждый вход сохранить input hash, точное целое optimum, minimizing full word, все cut widths этого word, число перечисленных words/cuts, ошибки и лимиты. Вход хешируется как JSON с sorted keys, compact separators, UTF-8 без BOM и без конечного LF; исходный порядок classes фиксируется input manifest.

До просмотра контрольных ответов исполнитель публикует hash исходников, dependencies/runtime, input manifest и exposure declaration: какие алгоритмы, доказательства и ответы он видел и когда. Сохранить полный журнал результатов. Если прочитал общий brief, candidate specification или ожидаемые ответы, это раскрывается; такой запуск не переименовывается в blinded.

От исполнителя не требуется изобретать сжатие или минимальную факторизацию. Его задача — точно решить полностью определённую исходную задачу без предположения корректности какого-либо сжатия. Математический вывод возможного сжатия относится к отдельному proof-review заданию.
```
