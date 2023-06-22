import base64
import hashlib
import sys
from pathlib import Path
from typing import List , Union

import schemas
from config import settings
from fastapi import UploadFile , Response
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
        
        # 1. all data blocks must exist
        for i in range(settings.NUM_DISKS):
            file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}" / filename
            if not file_path.is_file():
                logger.error(f"File: {file_path} does not exist")
                return False
        
        # 2. size of all data blocks must be equal
        file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-0" / filename
        file_size = file_path.stat().st_size
        for i in range(1, settings.NUM_DISKS):
            file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}" / filename
            if file_size != file_path.stat().st_size:
                logger.error(f"File: {file_path} size not equal")
                return False
        
        # 3. parity block must exist
        file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{settings.NUM_DISKS}" / filename
        if not file_path.is_file():
            logger.error(f"parity block File: {file_path} does not exist")
            return False
        
        # 4. parity verify must success
        raid_block_cnt=settings.NUM_DISKS-1
        block_list=[] # bytes list
        for i in range(raid_block_cnt):
            file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}" / filename
            with open(file_path, 'rb') as f:
                block_list.append(f.read())
                f.close()
        
        # parity block
        file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{settings.NUM_DISKS}" / filename
        parity_block_content=None
        with open(file_path, 'rb') as f:
            parity_block_content=f.read()
            f.close()

        # xor all block from block_list
        parity_content=block_list[0]
        for i in range(raid_block_cnt):
            parity_content=bytes(a ^ b for a, b in zip(parity_content, block_list[i]))

        if parity_content != parity_block_content:
            logger.error(f"parity block verify failed")
            return False

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
        if file_path.is_file():
            logger.error(f"File: {file_path} already exist")
            return HTTPException(status_code=409, detail="File already exist")
        
        # if file too large, response 413
        if len(content) > settings.MAX_SIZE:
            logger.error(f"File: {file_path} too large")
            return HTTPException(status_code=413, detail="File too large")
           
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
        padding_cnt=file_size%raid_block_cnt
        logger.info(f"block_size: { block_size }" )
        logger.info(f"raid block cnt: { (raid_block_cnt) }" )

        last_pos=0
        cur_pos=0
        block_list=[] # bytes list
        for i in range(raid_block_cnt):
            file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}" / file.filename

            if i < padding_cnt:
                cur_pos=last_pos+block_size+1
            
            logger.info(f"last_pos: {last_pos}, cur_pos: {cur_pos}")
            with open(file_path, 'wb') as f:
                # add padding
                logger.info(f"padding: {i<padding_cnt}")
                final_content=content_decode[last_pos:cur_pos]+int( i<padding_cnt ) * '\0'
                final_content_encode=final_content.encode(encoding='utf-8')
                block_list.append(final_content_encode)

                logger.info(f"file_path: {file_path}")
                logger.info(f"file content: { content_decode[last_pos:cur_pos] }")
                logger.info(f"file content+padding: { final_content }")
                logger.info(f"file encode: { final_content_encode }")
                f.write( final_content_encode )
                f.close()
            last_pos=cur_pos
            cur_pos=last_pos+block_size

        # parity block
        file_path = Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{settings.NUM_DISKS}" / file.filename
        logger.info(f"parity block file_path: {file_path}")
        with open(file_path, 'wb') as f:
            # xor all block from block_list
            parity_content=block_list[0]
            for i in range(1, len(block_list)):
                parity_content=bytes(a ^ b for a, b in zip(parity_content, block_list[i]))
            
            logger.info(f"parity block content: { parity_content }")
            f.write( parity_content )
            f.close()
        
            
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
