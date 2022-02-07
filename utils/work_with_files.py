import os, shutil
import zipfile


def delete_image(path):

    """ Удаляет изображение """

    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def unzip_files(number, WORK_DIR, uuid):

    """ Разорхивирует zip файл """

    unziped_pattern_dir = f'/unziped_files/{uuid}/{number}'
    
    zip_file = zipfile.ZipFile(f'{WORK_DIR}/dowanload_files/{uuid}/Response-{number}.zip')
    zip_file.extractall(path=WORK_DIR+f'/unziped_files/{uuid}/{number}')
    list_dir = os.listdir(WORK_DIR + unziped_pattern_dir)
    new_zip_file_path = []

    for dr in list_dir:
        if dr.split('.')[-1] == 'zip':
            new_zip_file_path.append(dr)
    if len(new_zip_file_path) != 0:
        path = new_zip_file_path[0]
        print(f'PATH: {path}')
    new_zip_file = zipfile.ZipFile(f'{WORK_DIR}/unziped_files/{uuid}/{number}/{path}')
    return_path = WORK_DIR + unziped_pattern_dir
    new_zip_file.extractall(path=return_path + '/')

    new_list_dir = os.listdir(WORK_DIR + unziped_pattern_dir)
    xml_file_path = []
    for dr in new_list_dir:
        if dr.split('.')[-1] == 'xml':
            xml_file_path.append(dr)
    print(xml_file_path)
    return return_path + f'/{xml_file_path[0]}'


def delete_files(number, WORK_DIR, uuid):

    """ Удаляет старые файлы """

    # os.remove(f'{WORK_DIR}/unziped_files/{number}')
    os.remove(f'{WORK_DIR}/dowanload_files/{uuid}/Response-{number}.zip')

