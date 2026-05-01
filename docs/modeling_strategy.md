# Modeling Strategy

## 1. Problem Formulation

본 문제는 DEPOT을 기준으로 여러 AGV가 작업 노드를 방문하는 Vehicle Routing Problem 계열 문제로 볼 수 있다. 각 작업은 좌표, service time, demand, deadline을 가지며, AGV는 speed, max distance, capacity 제약을 가진다.

## 2. Constraint Handling

capacity와 max distance는 tour 단위 hard constraint로 처리한다. deadline은 hard constraint로 강제하지 않고 objective function의 lateness penalty로 반영한다. 이 방식은 모든 작업을 할당하면서도 지연을 줄이는 방향으로 탐색을 유도한다.

## 3. ALNS

Adaptive Large Neighborhood Search 계열 구조를 사용한다. 매 iteration마다 일부 작업을 제거하고, 다시 삽입하며, simulated annealing 수용 규칙으로 지역 최적해 탈출을 허용한다.

## 4. Local Search

2-opt, relocate, swap, cross-exchange를 적용해 경로 내부 순서와 AGV 간 작업 배정을 개선한다.

## 5. Parallel Multi-seed

휴리스틱 최적화는 초기 난수와 탐색 경로에 민감하므로 여러 seed를 병렬 실행하고 가장 낮은 score를 갖는 해를 선택한다.
