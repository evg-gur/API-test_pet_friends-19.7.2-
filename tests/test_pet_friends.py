from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что при запросе api ключа выводится статус 200 и результат содержит слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев код статуса запроса 200 и список питомцев не пустой.
    Для этого сначала получаем api ключ, сохраняем его в переменную auth_key. После с помощью этого ключа
    проверяем статус ответа и то, что список питомцев не пустой."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Котэ', animal_type='кошка', age='1', pet_photo='images/котэ.jpg'):
    """Проверяем возможность добавления нового питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Котэ", "кошка", "1", "/котэ.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Машка', animal_type='Собака', age=1):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_api_key_with_wrong_email_and_correct_password(email=invalid_email, password=valid_password):
    """Негативный тест. Проверяем запрос с неверным email и правильным паролем. Проверяем отсутстсвие ключа в ответе"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    """Негативный тест. Проверяем запрос с верным email и неправильным паролем. Проверяем отсутствие ключа в ответе """

    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_add_pet_with_empty_value_in_variable_name(name='', animal_type='', age='', pet_photo=''):
    """Негативный тест: проверяем возможность добавления питомца с пустыми значениями переменных"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, api_key = pf.get_app_key(valid_email, valid_password)

    status, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name', 'animal_type', 'age', 'pet_photo'] != '', 'Питомец добавлен с пустыми значениями'


def test_add_pet_with_special_characters_in_animal_type(name='Котэ', age='-1', pet_photo='images/котэ.JPG'):
    """Негативный тест: проверяем возможность ввода в переменную animal_type символы вместо буквенных значений"""

    animal_type = '@&%!'
    symbols = '#$%^&*{}|?/><=+_~@'
    symbol = []

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, api_key = pf.get_app_key(valid_email, valid_password)
    status, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)

    assert status == 200
    for i in symbols:
        if i in result['animal_type']:
            symbol.append(i)
    assert symbol[0] not in result['animal_type'], 'Питомец добавлен с недопустимым значением'


def test_add_new_pet_negative_age(name='Котэ', animal_type='кошка', age='-1', pet_photo='images/котэ.JPG'):
    """Негативный тест: проверяем возможность добавления питомца с отрицательным числом в переменной age."""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert age not in result['age'], 'Питомец добавлен с отрицательным числом в поле возраст'


def test_add_new_pet_negative_number_age(name='Котэ', animal_type='кошка', age='некошка', pet_photo='images/котэ.JPG'):
    """Негативный тест: проверяем возможность ввода в переменныую age буквенные значения вместо числа"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert age not in result['age'], 'Питомец добавлен с недопустимым значением в поле возраст'


def test_add_pet_with_four_digit_age_number(name='Котэ', animal_type='кошка', age='4321', pet_photo='images/котэ.JPG'):
    """Негативный тест: проверяем возможность ввода в переменную age число более трех знаков"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, api_key = pf.get_app_key(valid_email, valid_password)
    _, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)
    number = result['age']

    assert len(number) < 4, 'Питомец добавлен с числом приевышающим 3 знака в поле возраст'


def test_add_pets_without_photo(name='Котэбезфотэ', animal_type='кот', age='4'):
    """Проверяем возможность добавления питомца без фото """

    _, api_key = pf.get_app_key(valid_email, valid_password)
    status, result = pf.add_pet_without_photo(api_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_add_pet_with_a_lot_of_words_is_name (animal_type = 'кошка', age='1', per_photo= 'images/котэ.JPG'):
    """Негативный тест: проверяем возможность ввода в переменную name более 13 слов"""

    name = 'АБВ гд еeeж зи йкл мн оп рст уф хц чшщ ъы ьэ юя'

    _, api_key = pf.get_app_key(valid_email, valid_password)
    status, result = pf.add_new_pets(api_key, name, animal_type, age, pet_photo)
    list_name = result['name'].split()
    word_count = len(list_name)

    assert status == 200
    assert word_count < 13, 'Питомец добавлен с именем больше 13 слов'