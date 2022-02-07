import os

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse

from utils.work_with_files import delete_image

app = FastAPI()


@app.get('/gibdd/api/v1/images/{image_uuid}')
def root_images(request: Request, background_tasks: BackgroundTasks, image_uuid: str):
    """ Получение изображений """

    try:
        file_path = f'./gibdd_parser/dtp_images/{image_uuid}'
        file_exist = os.path.exists(file_path)
        if file_exist:
            background_tasks.add_task(delete_image, file_path)
            return FileResponse(file_path)
        raise RuntimeError
    except RuntimeError:
        return JSONResponse(status_code=404,
                            content={'result': 'Fail', 'data': {'error': 'file not exist'}})
