import math
import random
import re
from html import escape

import streamlit as st


st.set_page_config(
    page_title="과자 공장 곱셈 탐험",
    page_icon="🍪",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #fffaf1; }
    .block-container { max-width: 1150px; padding-top: 1.5rem; }
    h1, h2, h3 { color: #573d35; }
    .hero {
        background: linear-gradient(120deg, #ffe8ad, #ffe2dc);
        border: 2px solid #f5d399; border-radius: 22px;
        padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    }
    .hero p { color: #644b3d; font-size: 1.08rem; margin-bottom: 0; }
    .order-card, .info-card {
        background: #fff; border: 2px solid #f1dfca; border-radius: 18px;
        padding: 1rem; text-align: center; margin: .35rem 0;
    }
    .order-card { min-height: 135px; }
    .order-card .big { font-size: 2rem; font-weight: 800; color: #69483c; }
    .order-card .label { color: #705c51; font-size: 1rem; }
    .candy-box {
        background: #fff; border: 2px solid #e6bd80; border-radius: 14px;
        padding: .65rem; margin: .3rem 0; text-align: center; min-height: 95px;
    }
    .box-title { color: #705c51; font-weight: 700; margin-bottom: .35rem; }
    .candy-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(25px, 1fr));
        gap: 2px; align-items: center; justify-items: center; font-size: 1.15rem;
    }
    .candy-count { color: #725440; font-weight: 800; margin-top: .35rem; }
    .ten-group {
        background: #fff0c9; border: 1px solid #e9c46b; border-radius: 9px;
        padding: .4rem; margin: .2rem; color: #694d26; font-weight: 700;
    }
    .math-expression {
        background: #fff0c9; border-radius: 16px; padding: 1rem;
        text-align: center; color: #503c2f; font-size: 1.65rem; font-weight: 800;
        margin: .5rem 0 1rem;
    }
    .area-cell {
        border: 2px solid #fff; border-radius: 12px; padding: .8rem .35rem;
        text-align: center; background: #dff3ea; color: #285744; min-height: 100px;
    }
    .area-cell.selected { background: #ffd98e; border-color: #e4a941; }
    .area-cell strong { display: block; font-size: 1.1rem; }
    .hint-card {
        background: #eef5ff; border-left: 5px solid #83aee8; border-radius: 10px;
        padding: .8rem 1rem; color: #344d6a;
    }
    @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .math-expression { font-size: 1.3rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SNACKS = {
    "초코 쿠키": "🍪",
    "딸기 도넛": "🍩",
    "젤리": "🍬",
    "막대 사탕": "🍭",
    "머핀": "🧁",
}

PROBLEM_TYPES = {
    "세 자리 수 × 한 자리 수": "hundreds",
    "몇십 × 몇십": "tens_tens",
    "몇십몇 × 몇십": "two_digit_tens",
    "몇 × 몇십몇": "one_digit_two_digit",
    "몇십몇 × 몇십몇": "two_digit_two_digit",
}


def new_order():
    return {
        "snack": random.choice(list(SNACKS)),
        "per_box": random.randint(4, 18),
        "boxes": random.randint(2, 7),
        "representation": random.choice(["그림", "묶음", "배열", "숫자", "혼합"]),
    }


def new_factors(problem_type, difficulty):
    limits = {
        "쉬움": (2, 5, 10, 59, 100, 399),
        "보통": (2, 7, 10, 89, 100, 699),
        "도전": (2, 9, 10, 99, 100, 999),
    }
    digit_min, digit_max, two_min, two_max, hundreds_min, hundreds_max = limits[
        difficulty
    ]
    kind = PROBLEM_TYPES[problem_type]

    if kind == "hundreds":
        return random.randint(hundreds_min, hundreds_max), random.randint(
            digit_min, digit_max
        )
    if kind == "tens_tens":
        return random.randint(1, 9) * 10, random.randint(1, 9) * 10
    if kind == "two_digit_tens":
        return random.randint(two_min, two_max), random.randint(1, 9) * 10
    if kind == "one_digit_two_digit":
        return random.randint(digit_min, digit_max), random.randint(two_min, two_max)
    return random.randint(two_min, two_max), random.randint(two_min, two_max)


def draw_box(count, snack, label, mode, columns=6):
    emoji = SNACKS[snack]
    contents = []
    if mode == "숫자":
        contents = [f"<div class='candy-count'>{count}개</div>"]
    elif mode == "묶음":
        tens, ones = divmod(count, 10)
        contents.extend(
            f"<div class='ten-group'>10개 묶음 {emoji * 10}</div>" for _ in range(tens)
        )
        if ones:
            contents.append(
                f"<div class='candy-grid'>{emoji * ones}</div>"
            )
        if count == 0:
            contents.append("<div class='candy-count'>과자가 없어요</div>")
    else:
        grid = (
            f"<div class='candy-grid' style='grid-template-columns:repeat("
            f"{min(columns, max(1, count))}, minmax(20px, 1fr))'>"
            f"{emoji * count}</div>"
        )
        contents.append(grid)
        if mode == "배열":
            rows = math.ceil(count / max(1, columns))
            contents.append(
                f"<div class='candy-count'>{rows}줄로 놓았어요</div>"
            )
    return (
        "<div class='candy-box'>"
        f"<div class='box-title'>{escape(label)}</div>"
        f"{''.join(contents)}"
        f"<div class='candy-count'>한 상자에 {count}개</div>"
        "</div>"
    )


def show_boxes(box_counts, snack, mode, columns=6):
    cols_per_row = 4
    for start in range(0, len(box_counts), cols_per_row):
        cols = st.columns(min(cols_per_row, len(box_counts) - start))
        for offset, col in enumerate(cols):
            box_index = start + offset
            with col:
                st.markdown(
                    draw_box(
                        box_counts[box_index],
                        snack,
                        f"{box_index + 1}번 상자",
                        mode,
                        columns,
                    ),
                    unsafe_allow_html=True,
                )


def split_by_place_value(number):
    parts = []
    place = 10 ** (len(str(number)) - 1)
    remainder = number
    while place:
        digit_value = (remainder // place) * place
        if digit_value:
            parts.append(digit_value)
        remainder %= place
        place //= 10
    return parts


def decomposition(first, second):
    first_parts = split_by_place_value(first)
    second_parts = split_by_place_value(second)
    terms = [
        (left, right, left * right)
        for left in first_parts
        for right in second_parts
    ]
    return first_parts, second_parts, terms


def show_calculation(first, second, selected_index=None):
    first_parts, second_parts, terms = decomposition(first, second)
    st.markdown(
        f"<div class='math-expression'>{first} × {second} = "
        f"({ ' + '.join(map(str, first_parts)) }) × "
        f"({ ' + '.join(map(str, second_parts)) })</div>",
        unsafe_allow_html=True,
    )
    if len(terms) == 1:
        left, right, product = terms[0]
        st.markdown(
            f"<div class='area-cell selected'><strong>{left} × {right}</strong>"
            f"{product}개</div>",
            unsafe_allow_html=True,
        )
        st.caption("각 묶음의 수와 묶음 개수를 곱해요.")
        return

    st.markdown("#### 자릿값끼리 곱해 볼까요?")
    cols = st.columns(len(terms))
    for index, (left, right, product) in enumerate(terms):
        selected = index == selected_index
        with cols[index]:
            st.markdown(
                f"<div class='area-cell {'selected' if selected else ''}'>"
                f"<strong>{left} × {right}</strong>{product}개</div>",
                unsafe_allow_html=True,
            )
    partial_sum = " + ".join(str(term[2]) for term in terms)
    st.markdown(
        f"<div class='math-expression' style='font-size:1.25rem'>"
        f"부분곱을 더하면: {partial_sum} = {first * second}</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "십, 백의 자리 수를 따로 곱한 뒤 부분곱을 모두 더하면 전체 과자 수예요."
    )


def draw_order(order):
    snack = order["snack"]
    per_box = order["per_box"]
    boxes = order["boxes"]
    mode = order["representation"]

    st.markdown(
        f"<div class='math-expression'>한 상자에 {per_box}개씩, "
        f"{boxes}상자 포장하기</div>",
        unsafe_allow_html=True,
    )
    if mode in ("그림", "배열"):
        show_boxes([per_box] * boxes, snack, mode, columns=6)
    elif mode == "묶음":
        tens, ones = divmod(per_box, 10)
        st.write(f"과자 종류: {SNACKS[snack]} {snack}")
        st.markdown(
            f"<div class='info-card'>상자 하나에 "
            f"{' + '.join([f'10개 묶음 {tens}개'] if tens else [])}"
            f"{' + ' if tens and ones else ''}"
            f"{f'낱개 {ones}개' if ones else ''}가 들어 있어요. "
            f"이 상자가 {boxes}개예요.</div>",
            unsafe_allow_html=True,
        )
    elif mode == "숫자":
        st.markdown(
            f"<div class='order-card'><div class='big'>"
            f"{per_box}개 × {boxes}상자</div>"
            f"<div class='label'>{SNACKS[snack]} {snack}를 포장해요</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.write(f"과자 종류: {SNACKS[snack]} {snack}")
        st.markdown(
            f"<div class='info-card'>"
            f"{draw_box(per_box, snack, '한 상자의 과자', '그림')}"
            f"<strong>이 상자 {boxes}개를 포장해요.</strong></div>",
            unsafe_allow_html=True,
        )
    st.caption(f"이번 주문은 '{mode}' 표현으로 나타냈어요.")


if "order" not in st.session_state:
    st.session_state.order = new_order()
if "sim_boxes" not in st.session_state:
    st.session_state.sim_boxes = 4
if "sim_per_box" not in st.session_state:
    st.session_state.sim_per_box = 12
if "explore_type" not in st.session_state:
    st.session_state.explore_type = next(iter(PROBLEM_TYPES))
if "explore_problem" not in st.session_state:
    st.session_state.explore_problem = new_factors(
        st.session_state.explore_type, "보통"
    )
if "challenge_type" not in st.session_state:
    st.session_state.challenge_type = next(iter(PROBLEM_TYPES))
if "challenge_difficulty" not in st.session_state:
    st.session_state.challenge_difficulty = "쉬움"
if "challenge_problem" not in st.session_state:
    st.session_state.challenge_problem = new_factors(
        st.session_state.challenge_type, st.session_state.challenge_difficulty
    )

st.markdown(
    "<div class='hero'><h1>🍪 과자 공장 곱셈 탐험</h1>"
    "<p>공장 직원이 되어 상자에 과자를 담고, 곱셈의 비밀을 찾아봐요!</p></div>",
    unsafe_allow_html=True,
)

activity = st.radio(
    "오늘의 활동",
    [
        "1. 주문서 확인",
        "2. 포장 실험실",
        "3. 계산 원리 탐구",
        "4. 새 주문 해결",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

if activity == "1. 주문서 확인":
    st.header("📋 오늘의 주문서")
    st.write("주문을 살펴보고, 상자에 들어갈 과자 수를 먼저 예상해 보세요.")
    if st.button("🔄 새로운 주문 받기", type="secondary"):
        st.session_state.order = new_order()
        st.session_state.pop("order_estimate", None)
    order = st.session_state.order
    summary = st.columns(3)
    with summary[0]:
        st.markdown(
            f"<div class='order-card'><div class='big'>{SNACKS[order['snack']]}</div>"
            f"<div class='label'>{order['snack']}</div></div>",
            unsafe_allow_html=True,
        )
    with summary[1]:
        st.markdown(
            f"<div class='order-card'><div class='big'>{order['per_box']}개</div>"
            "<div class='label'>한 상자에 담을 과자</div></div>",
            unsafe_allow_html=True,
        )
    with summary[2]:
        st.markdown(
            f"<div class='order-card'><div class='big'>{order['boxes']}상자</div>"
            "<div class='label'>포장할 상자</div></div>",
            unsafe_allow_html=True,
        )
    draw_order(order)
    st.subheader("전체 과자는 몇 개일까요?")
    estimate = st.number_input(
        "먼저 어림한 수를 적어 보세요.",
        min_value=0,
        max_value=9999,
        step=1,
        key="order_estimate",
    )
    if st.button("예상한 수 확인하기", type="primary"):
        actual = order["per_box"] * order["boxes"]
        st.info(
            f"내 예상은 {estimate}개예요. 상자마다 과자가 몇 개씩 있는지 세어 "
            "곱셈식으로 확인해 봐요!"
        )
        st.markdown(
            f"<div class='math-expression'>{order['per_box']} × "
            f"{order['boxes']} = {actual}개</div>",
            unsafe_allow_html=True,
        )

elif activity == "2. 포장 실험실":
    st.header("🧪 과자 포장 실험실")
    st.write("상자 수와 상자마다 담을 과자 수를 바꾸거나, 상자 사이로 과자를 옮겨 보세요.")
    if st.button("↩️ 실험 초기화"):
        st.session_state.sim_boxes = 4
        st.session_state.sim_per_box = 12
        st.session_state.sim_box_counts = [12] * 4
        st.session_state.sim_distribution_settings = (4, 12)
        st.session_state.transfer_source = 0
        st.session_state.transfer_destination = 1
        st.session_state.transfer_amount = 1
    controls = st.columns(2)
    with controls[0]:
        st.slider("포장할 상자 수", 1, 8, key="sim_boxes")
    with controls[1]:
        st.slider("한 상자에 담을 과자 수", 1, 30, key="sim_per_box")
    mode = st.radio(
        "과자를 어떻게 볼까요?",
        ["그림", "묶음", "배열", "숫자"],
        horizontal=True,
        key="sim_representation",
    )
    boxes = st.session_state.sim_boxes
    per_box = st.session_state.sim_per_box
    settings = (boxes, per_box)
    if st.session_state.get("sim_distribution_settings") != settings:
        st.session_state.sim_box_counts = [per_box] * boxes
        st.session_state.sim_distribution_settings = settings
        st.session_state.transfer_source = 0
        st.session_state.transfer_destination = 1 if boxes > 1 else 0
        st.session_state.transfer_amount = 1

    box_counts = st.session_state.sim_box_counts
    total = sum(box_counts)
    st.markdown(
        f"<div class='math-expression'>{per_box}개 × {boxes}상자 "
        f"= {total}개</div>",
        unsafe_allow_html=True,
    )
    st.markdown("#### 과자를 다른 상자로 옮겨 볼까요?")
    if boxes < 2:
        st.info("상자가 두 개 이상 있어야 과자를 옮길 수 있어요.")
    else:
        transfer_cols = st.columns(3)
        with transfer_cols[0]:
            source = st.selectbox(
                "어느 상자에서?",
                range(boxes),
                format_func=lambda index: (
                    f"{index + 1}번 상자 ({box_counts[index]}개)"
                ),
                key="transfer_source",
            )
        with transfer_cols[1]:
            destination = st.selectbox(
                "어느 상자로?",
                range(boxes),
                format_func=lambda index: (
                    f"{index + 1}번 상자 ({box_counts[index]}개)"
                ),
                key="transfer_destination",
            )
        available = box_counts[source]
        amount_options = list(range(1, available + 1)) if available else [0]
        if st.session_state.get("transfer_amount") not in amount_options:
            st.session_state.transfer_amount = amount_options[0]
        with transfer_cols[2]:
            amount = st.selectbox(
                "몇 개 옮길까요?",
                amount_options,
                format_func=lambda count: f"{count}개",
                key="transfer_amount",
                disabled=available == 0,
            )
        if st.button("➡️ 과자 옮기기", type="primary"):
            if source == destination:
                st.warning("서로 다른 상자를 골라 주세요.")
            elif amount == 0:
                st.warning("옮길 과자가 없어요. 다른 상자를 골라 보세요.")
            else:
                box_counts[source] -= amount
                box_counts[destination] += amount
                st.session_state.sim_box_counts = box_counts
                st.rerun()

    show_boxes(box_counts, "초코 쿠키", mode)
    st.success(
        f"모두 {total}개예요. 상자 사이로 옮겨도 전체 과자 수는 변하지 않아요."
    )

elif activity == "3. 계산 원리 탐구":
    st.header("🔎 곱셈의 계산 원리 탐구")
    problem_type = st.selectbox(
        "탐구할 곱셈 유형",
        list(PROBLEM_TYPES),
        key="explore_type",
    )
    if st.session_state.get("last_explore_type") != problem_type:
        st.session_state.explore_problem = new_factors(problem_type, "보통")
        st.session_state.last_explore_type = problem_type
    if st.button("🎲 다른 숫자로 다시 탐구하기"):
        st.session_state.explore_problem = new_factors(problem_type, "보통")
    first, second = st.session_state.explore_problem
    first_parts, second_parts, terms = decomposition(first, second)
    if len(terms) > 1:
        term_labels = [
            f"{left} × {right} = {product}"
            for left, right, product in terms
        ]
        selected_label = st.selectbox("자릿값 곱을 골라 강조해요", term_labels)
        selected_index = term_labels.index(selected_label)
    else:
        selected_index = None
    show_calculation(first, second, selected_index)
    st.markdown(
        f"<div class='info-card'>"
        f"{SNACKS['초코 쿠키']} 과자를 상자에 담는다고 생각해 보세요. "
        f"{first}와 {second}를 자릿값으로 나누어 각각 곱하면 "
        "큰 곱셈도 작은 곱셈으로 나누어 계산할 수 있어요.</div>",
        unsafe_allow_html=True,
    )

else:
    st.header("📦 새로운 주문 해결하기")
    st.write("문제를 읽고 곱셈식과 답을 직접 입력해 보세요.")
    controls = st.columns(2)
    with controls[0]:
        problem_type = st.selectbox(
            "문제 유형",
            list(PROBLEM_TYPES),
            key="challenge_type",
        )
    with controls[1]:
        difficulty = st.selectbox(
            "난이도",
            ["쉬움", "보통", "도전"],
            key="challenge_difficulty",
        )
    if (
        st.session_state.get("last_challenge_type") != problem_type
        or st.session_state.get("last_challenge_difficulty") != difficulty
    ):
        st.session_state.challenge_problem = new_factors(problem_type, difficulty)
        st.session_state.last_challenge_type = problem_type
        st.session_state.last_challenge_difficulty = difficulty
        st.session_state.pop("student_expression", None)
        st.session_state.pop("student_answer", None)
    if st.button("🎲 새 문제 받기"):
        st.session_state.challenge_problem = new_factors(problem_type, difficulty)
        st.session_state.pop("student_expression", None)
        st.session_state.pop("student_answer", None)

    first, second = st.session_state.challenge_problem
    snack = random.Random(f"{first}-{second}").choice(list(SNACKS))
    st.markdown(
        f"<div class='math-expression'>{SNACKS[snack]} {snack} "
        f"{first}개씩 {second}상자를 포장해요.<br>"
        "모두 몇 개를 포장해야 할까요?</div>",
        unsafe_allow_html=True,
    )
    with st.form("answer_form"):
        expression = st.text_input(
            "곱셈식을 써 보세요. 예: 24 × 13",
            key="student_expression",
            placeholder="두 수와 곱셈 기호를 입력해요",
        )
        answer = st.number_input(
            "계산한 답",
            min_value=0,
            max_value=99999,
            step=1,
            key="student_answer",
        )
        submitted = st.form_submit_button("정답 확인하기", type="primary")

    if submitted:
        compact_expression = re.sub(r"\s+", "", expression)
        match = re.fullmatch(r"(\d+)(?:×|x|X|\*)(\d+)", compact_expression)
        if match is None:
            st.warning("곱셈식을 숫자와 × 기호로 써 주세요. 예: 24 × 13")
        else:
            entered_factors = (int(match.group(1)), int(match.group(2)))
            if entered_factors != (first, second):
                st.warning("문제에 나온 두 수를 순서대로 곱셈식에 넣어 보세요.")
            elif int(answer) == first * second:
                st.success("정답이에요! 🎉 정확하게 포장했어요. 멋져요!")
            else:
                st.warning("아직 답이 달라요. 정답은 잠시 숨겨 둘게요.")
                first_parts = split_by_place_value(first)
                second_parts = split_by_place_value(second)
                st.markdown(
                    f"<div class='hint-card'>힌트: {first}를 "
                    f"{' + '.join(map(str, first_parts))}로 나누고, "
                    f"{second}도 {' + '.join(map(str, second_parts))}로 나누어 "
                    "부분곱을 구한 뒤 모두 더해 보세요.</div>",
                    unsafe_allow_html=True,
                )
                show_calculation(first, second)
