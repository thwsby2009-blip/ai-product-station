from modules import lesson_0, lesson_1, lesson_420, lesson_427, colab

lesson_map = {
    "lesson_0": lesson_0,
    "lesson_1": lesson_1,
    "lesson_420": lesson_420,
    "lesson_427": lesson_427,
    "colab": colab
}

lesson_map[lesson].run()
