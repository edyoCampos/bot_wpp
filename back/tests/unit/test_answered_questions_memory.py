from robbot.services.answered_questions import AnsweredQuestionsMemory


def test_add_and_check_answered():
    mem = AnsweredQuestionsMemory()
    mem.add("Quanto custa a consulta?")
    assert mem.was_answered("Quanto custa a consulta?")
    assert mem.was_answered("quanto custa a consulta?")
    assert mem.was_answered("  Quanto custa a consulta?  ")
    assert not mem.was_answered("Quais os horários?")


def test_normalization():
    mem = AnsweredQuestionsMemory()
    mem.add("Qual o endereço?")
    assert mem.was_answered("qual o endereço?")
    assert not mem.was_answered("Qual o endereco?")  # Different word


def test_reset():
    mem = AnsweredQuestionsMemory()
    mem.add("Pergunta 1?")
    mem.reset()
    assert not mem.was_answered("Pergunta 1?")
