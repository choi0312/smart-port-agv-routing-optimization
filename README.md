# Smart Port AGV Routing Optimization

스마트 항만 환경에서 AGV가 주어진 작업을 제한 시간 내에 효율적으로 수행하도록 경로를 최적화하는 휴리스틱 최적화 프로젝트입니다.

본 저장소는 DACON의 **스마트 해운물류 x AI 미션 챌린지 : 스마트 항만 AGV 경로 최적화 경진대회** 참가 코드를 모듈형 Python 프로젝트로 재구성한 버전입니다. 기존 단일 스크립트 형태의 ALNS 풀이를 데이터 로딩, 제약 검증, 목적함수, 초기해 생성, destroy/repair 연산자, local search, 병렬 multi-seed 실행, 제출 파일 생성 모듈로 분리했습니다.

## Competition Result

| 항목 | 내용 |
|---|---|
| 대회명 | 스마트 해운물류 x AI 미션 챌린지 : 스마트 항만 AGV 경로 최적화 경진대회 |
| 플랫폼 | DACON |
| 문제 유형 | 정형 최적화, AGV Routing, VRP/TSP 변형 |
| 성과 | 예선 리더보드 6등 |
| 최종 점수 | 12,563 |
| 대회 링크 | https://dacon.io/competitions/official/236592/leaderboard |

## 1. 문제 정의

입력 데이터는 작업 정보와 AGV 사양으로 구성됩니다.

- task.csv: 작업 ID, 좌표, 서비스 시간, 수요량, deadline
- agv.csv: AGV ID, 이동 속도, 최대 주행거리, 적재 용량

목표는 모든 작업을 AGV 경로에 배정하면서 총 이동시간, 서비스 시간, deadline 지연 패널티를 최소화하는 것입니다.

## 2. 핵심 제약

| 제약 | 설명 |
|---|---|
| Depot 출발/복귀 | 각 AGV route는 DEPOT에서 출발하고 DEPOT으로 복귀 |
| 적재 용량 | 각 tour의 총 demand가 AGV capacity를 초과하지 않아야 함 |
| 최대 주행거리 | 각 tour의 Manhattan distance가 AGV max_distance를 초과하지 않아야 함 |
| 빈손 왕복 방지 | 작업이 없는 DEPOT-DEPOT tour는 제출에서 제거 |
| Deadline | hard constraint가 아닌 objective penalty로 처리 |

## 3. 목적함수

<pre>
score = total_travel_time + total_service_time + lambda * total_lateness
</pre>

이동시간은 Manhattan distance를 AGV별 speed로 나누어 계산합니다. Deadline 위반은 soft penalty로 처리하여 feasibility를 유지하면서도 지연을 억제합니다.

## 4. 접근 전략

| 단계 | 전략 |
|---|---|
| 초기해 | deadline이 빠른 작업부터 greedy insertion |
| Destroy | random removal, worst lateness removal, Shaw relatedness removal |
| Repair | safe insertion, regret-k insertion |
| Local Search | 2-opt, relocate, swap, cross-exchange |
| Acceptance | simulated annealing 기반 확률적 수용 |
| Multi-seed | 여러 seed를 병렬 실행한 뒤 최적해 선택 |
| Submission | AGV별 route를 DACON 제출 형식으로 저장 |

## 5. 저장소 구조

<pre>
smart-port-agv-routing-optimization/
├─ configs/
│  └─ default.yaml
├─ src/
│  └─ agv_optimizer/
│     ├─ config.py
│     ├─ data.py
│     ├─ solution.py
│     ├─ scoring.py
│     ├─ initial.py
│     ├─ destroy.py
│     ├─ repair.py
│     ├─ local_search.py
│     ├─ alns.py
│     ├─ submission.py
│     └─ pipeline.py
├─ scripts/
│  └─ run_optimizer.py
├─ tests/
├─ docs/
├─ reports/
├─ README.md
└─ requirements.txt
</pre>

## 6. 실행 방법

### 6.1 데이터 배치

대회 데이터는 저장소에 포함하지 않습니다. 아래 경로에 직접 배치합니다.

<pre>
data/raw/task.csv
data/raw/agv.csv
</pre>

### 6.2 패키지 설치

<pre>
pip install -r requirements.txt
</pre>

### 6.3 최적화 실행

<pre>
python scripts/run_optimizer.py --config configs/default.yaml
</pre>

### 6.4 출력 파일

<pre>
outputs/
├─ submission.csv
├─ run_summary.json
└─ seed_results.csv
</pre>

## 7. 설계 의도

이 프로젝트는 단순히 제출 스크립트를 올리는 대신, 다음 역량이 드러나도록 구성했습니다.

- AGV routing 문제를 VRP/TSP 변형 최적화 문제로 구조화
- hard constraint와 soft deadline penalty를 분리
- destroy/repair 연산자를 모듈화해 ALNS 구조를 명확히 표현
- local search를 별도 모듈로 분리해 개선 단계 재사용성 확보
- multi-seed 병렬 실행으로 stochastic heuristic의 탐색 안정성 확보
- 제출 포맷 생성과 최적화 로직 분리
