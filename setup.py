import subprocess
import re
import os

'''
Проверка на запуск скрипта от рут-пользователя
'''


def is_root():
    return os.geteuid() == 0


'''
Вызывая процесс lsusb, получаем список доступных USB-устройств
'''


def get_avaible_device():
    lsusb_process = subprocess.Popen(
        ["lsusb"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lsusb_process_stdout, lsusb_process_error = [
        x.decode('utf-8') for x in lsusb_process.communicate()]

    if lsusb_process.poll() != 0:
        raise Exception(f"Error: ${lsusb_process_error}")

    avaible_devices = lsusb_process_stdout.split('\n')[0:-1]
    return(avaible_devices)


'''
Меню для выбора пользователем доверенного устройства
'''


def select_device(avaible_devices):
    print("Select a trusted device\nAvaible devices:")
    for i, device in enumerate(avaible_devices):
        print(f"{i}) {device}")

    trusted_device_index = 0
    try:
        trusted_device_index = int(input("Enter the number of device: "))
        if trusted_device_index > len(avaible_devices) - 1:
            raise ValueError
    except ValueError:
        print("Sorry, this index id unavaible")

    return(avaible_devices[trusted_device_index])


'''
Получаем название устройства и его уникальные индентификаторы
'''


def get_device_id(device):
    print(device)
    device_re = re.compile(
        b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<VendorId>\w+):(?P<ProductId>\w+)\s(?P<tag>.+)$", re.I)
    device_info = device_re.match(str.encode(device))
    if not device_info:
        raise Exception(f"Error Unexpected device: {device}")
    parsed_device_info = device_info.groupdict()

    device_id = int(device_info.groupdict()['VendorId'].decode(
        'utf-8'), 16), int(parsed_device_info['ProductId'].decode('utf-8'), 16), parsed_device_info['device'].decode('utf-8')
    return device_id


'''
Вызываем сборку проектов при помощи Makefile
'''


def make_build():
    make_process = subprocess.Popen(
        ["make"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    make_process_stdout, make_process_error = [
        x.decode('utf-8') for x in make_process.communicate()]

    if make_process.poll() != 0:
        raise Exception(f"Error make: {make_process_error}")
    return


'''
Удаляем временные файлы после сборки
'''


def make_clean():
    make_process = subprocess.Popen(
        ["make clean"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    make_process_stdout, make_process_error = [
        x.decode('utf-8') for x in make_process.communicate()]

    if make_process.poll() != 0:
        raise Exception(f"Error make clean: {make_process_error}")
    return


'''
Выгружаем модуль ядра
'''


def unload_module():
    rm_module_process = subprocess.Popen(
        ["modprobe -r usb_key"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rm_module_process_stdout, rm_module_process_stderr = [
        x.decode('utf-8') for x in rm_module_process.communicate()]

    if rm_module_process.poll() != 0:
        raise Exception(f"modprobe -r usb_key: {rm_module_process_stderr}")

    return


'''
Подгружаем модуль ядра, добавляя его зависимости в modules.dep
'''


def load_module():
    depmod_process = subprocess.Popen(
        ["depmod"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    depmod_process_stdout, depmod_process_stderr = depmod_process.communicate()

    if depmod_process.poll() != 0:
        raise Exception(f"Error depmod: {depmod_process_stderr}")

    modprobe_process = subprocess.Popen(
        ["modprobe usb_key"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    modprobe_process_stdout, modprobe_process_stderr = modprobe_process.communicate()

    if modprobe_process.poll() != 0:
        raise Exception(f"Error modprobe usb_key: {modprobe_process_stderr}")

    return


'''
Функиция генерации ключа для шифрования
'''


def generate_key():
    return os.urandom(24).hex()


'''
Сохранение ключа в указанную директорию
'''


def save_key(filepath, key):
    with open(filepath+"/.key", "w") as file:
        file.write(key)


'''
Меню для выбора пользователем пути для сохранения ключа
'''


def get_encryption_key_path():
    path = input("Enter the path to save the encryption key: ")

    while not os.path.exists(path):
        path = input(f"This path doesn't exists. Try again: ")
    return path


'''
Функция валидации на существование путей файлов для шифрования
'''


def validate_paths():
    paths = []
    while True:
        try:
            paths.append(input())
        except EOFError:
            break

    for path in paths:
        if not os.path.exists(path):
            print(f"This path doesn't exists {path}")
            paths.remove(path)
    return paths


'''
Меню для ввода пользователем защищаемых файлов
'''


def get_encryption_path():
    print("Enter the encryption file paths line by line:")
    paths = validate_paths()
    while len(paths) == 0:
        print(f"Zero valid paths have been entered. Try again")
        paths = validate_paths()
    return paths


'''
Сохраняем конфигурацию
'''


def save_config(device, encryption_paths, key_path, key):
    cur_config = ""
    updated_config = ""
    with open('config.template', 'r') as f:
        cur_config = f.read()

    IdVendor_template, IdProduct_template, name_template = device
    cur_config = cur_config.replace('key_path_template', key_path)
    cur_config = cur_config.replace(
        '"IdVendor_template"', str(IdVendor_template))
    cur_config = cur_config.replace(
        '"IdProduct_template"', str(IdProduct_template))
    updated_config = cur_config.replace('name_template', name_template)

    with open('config.h', 'w') as f:
        f.write(updated_config)

    cur_config = ""
    updated_config = ""
    with open('crypto_config.template', 'r') as f:
        cur_config = f.read()

    cur_config = cur_config.replace('key_template', key)
    paths = [f'"{x}"' for x in encryption_paths]
    updated_config = cur_config.replace(
        '"encryption_paths_tempalate"', ",".join(paths))

    with open('crypto_config.h', 'w') as f:
        f.write(updated_config)


def main():
    if not is_root():
        print("You need root permissions to do this")
        return
    avaible_devices = get_avaible_device()
    device = get_device_id(select_device(avaible_devices))

    encryption_paths = get_encryption_path()
    key_path = get_encryption_key_path()
    key = generate_key()
    save_key(key_path, key)
    print("Encryption key genenerated and saved on the device")

    save_config(device, encryption_paths, key_path, key)

    unload_module()
    make_build()
    load_module()
    print("Kernel module successfully loaded")
    make_clean()


if __name__ == "__main__":
    main()
