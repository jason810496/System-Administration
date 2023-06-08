import base64
import hashlib
import sys
from pathlib import Path
from typing import List

import schemas
from config import settings
from fastapi import UploadFile
from loguru import logger
from starlette.exceptions import HTTPException


class Storage:
    def __init__(self, is_test: bool):
        self.block_path: List[Path] = [
            Path("/tmp") / f"{settings.FOLDER_PREFIX}-{i}-test"
            if is_test
            else Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}"
            for i in range(settings.NUM_DISKS)
        ]
        self.__create_block()

    def __create_block(self):
        for path in self.block_path:
            logger.warning(f"Creating folder: {path}")
            path.mkdir(parents=True, exist_ok=True)

    async def file_integrity(self, filename: str) -> bool:
        """TODO: check if file integrity is valid
        file integrated must satisfy following conditions:
            1. all data blocks must exist
            2. size of all data blocks must be equal
            3. parity block must exist
            4. parity verify must success

        if one of the above conditions is not satisfied
        the file does not exist
        and the file is considered to be damaged
        so we need to delete the file
        """


        return True

    async def create_file(self, file: UploadFile) -> schemas.File:
        # TODO: create file with data block and parity block and return it's schema
        
        file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-0" / file.filename 
        content = await file.read()
        # with open(file_path, 'wb') as f:
        #     content = await file.read()
        #     f.write(content)
        #     f.close()
       

        # if file already exist, response 409
        # if file_path.is_file():
        #     return HTTPException(status_code=409, detail="File already exist")
        
        # # if file too large, response 413
        # if len(content) > settings.MAX_SIZE:
        #     return HTTPException(status_code=413, detail="File too large")
           
        import os # for getsize 

        file_size=len(content) # before decode

        content_decode=content.decode(encoding='utf-8') # normal string
        content_encode=content_decode.encode(encoding='utf-8')

        logger.info(f"check file_path {os.path.isfile(file_path)} ")
        logger.info(f"File: {file_path} created")
        logger.info(f"content: { content }" )
        logger.info(f"content len : { len(content) }" )
        logger.info(f"content.decode: { content_decode }" )
        logger.info(f"content.decode len: { len(content_decode) }" )
        logger.info(f"size: { file_size }" )
        logger.info(f"checksum: {hashlib.md5(content_encode).hexdigest()} " )

        # store to raid ( /var/raid/block-0 )
        raid_block_cnt=settings.NUM_DISKS-1

        import math
        block_size=file_size//raid_block_cnt
        logger.info(f"block_size: { block_size }" )
        logger.info(f"raid block cnt: { (raid_block_cnt) }" )

        last_pos=0
        cur_pos=block_size+1
        first_block_size=block_size+1
        for i in range(raid_block_cnt):
            file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}" / file.filename
            
            logger.info(f"last_pos: {last_pos}, cur_pos: {cur_pos}")
            with open(file_path, 'wb') as f:
                # add padding
                logger.info(f"padding: {first_block_size-cur_pos+last_pos}")
                padding=first_block_size-cur_pos+last_pos
                final_content=content_decode[last_pos:cur_pos]+padding * '\0'
                final_content_encode=final_content.encode(encoding='utf-8')
                logger.info(f"file_path: {file_path}")
                logger.info(f"file content: { content_decode[last_pos:cur_pos] }")
                logger.info(f"file encode: { final_content }")
                f.write( final_content_encode )
                f.close()
            last_pos=cur_pos
            cur_pos=last_pos+block_size
        
            
        # response
        return schemas.File(
            name=file.filename,
            size=file_size,
            checksum=hashlib.md5(content_encode).hexdigest(),
            content=base64.b64encode( bytes(content_decode, 'utf-8') ),
            content_type="text/plain",
        )

    async def retrieve_file(self, filename: str) -> bytes:
        # TODO: retrieve the binary data of file

        file_path = Path(settings.UPLOAD_PATH) / filename
        print(file_path)
        with open(file_path, 'rb') as file:
            binary_data = file.read()

        return binary_data

    async def update_file(self, file: UploadFile) -> schemas.File:
        # TODO: update file's data block and parity block and return it's schema

        file_content = await file.read()

        # Update file's data block and parity block (implement your logic here)
        # ...

        # Generate checksum
        checksum = hashlib.md5(file_content).hexdigest()

        # Prepare the response
        response = schemas.File(
            name=file.filename,
            size=len(file_content),
            checksum=checksum,
            content=base64.b64encode(file_content),
            content_type=file.content_type,
        )

        # Save the updated content to the file on disk
        file_path = Path(settings.UPLOAD_PATH) / file.filename
        with open( file_path, 'wb') as f:
            f.write(file_content)

        return response

    async def delete_file(self, filename: str) -> None:
        # TODO: delete file's data block and parity block

        file_path = Path(settings.UPLOAD_PATH) / filename
        file_path.unlink()

    async def fix_block(self, block_id: int) -> None:
        # TODO: fix the broke block by using rest of block

        pass


storage: Storage = Storage(is_test="pytest" in sys.modules)
