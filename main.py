import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import yt_dlp
from starlette.concurrency import run_in_threadpool
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

print(os.getenv("BGUTIL"))

if os.getenv("BGUTIL") == "1":
    mp3_opts = {
            "format" :"bestaudio/best",
            "extractor_args": {
                "youtube": {
                    "botguard_client_params": "base_url=http://127.0.0.1:4416"
                }
            },
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }],
            "outtmpl": "%(title)s.%(ext)s"
        }
    
    mp4_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "extractor_args": {
            "youtube": {
                "botguard_client_params": "base_url=http://127.0.0.1:4416"
            }
        },
        "merge_output_format": "mp4",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
        "outtmpl": "%(title)s.%(ext)s"
    }

elif os.getenv("BGUTIL") == "0":

    mp3_opts = {
                "format" :"bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }],
                "outtmpl": "%(title)s.%(ext)s"
            }
    mp4_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }],
            "outtmpl": "%(title)s.%(ext)s"
    }

else:
    print("please put a 'BGUTIL' variable, if you already put it in the .env file pls make it 0 or 1")
    print("press enter to quit..")
    input()
    sys.exit()

def downloadpm3(link: str):
    if not "https://youtu.be/" in link and not "https://www.youtube.com/watch" in link and not "https://youtube.com/shorts/" in link:
        raise HTTPException(400, detail="the link must be a youtube video or a youtube short.")
    
    try:
        ytdlp = yt_dlp.YoutubeDL(mp3_opts)
        info = ytdlp.extract_info(link, download=True)
        rawfilename = ytdlp.prepare_filename(info)
        title = os.path.splitext(rawfilename)[0]
        filename = f"{title}.mp3"
        return filename

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def downloadmp4(link: str):
    if not "https://youtu.be/" in link and not "https://www.youtube.com/watch" in link and not "https://youtube.com/shorts/" in link:
        raise HTTPException(400, detail="the link must be a youtube video or a youtube short.")

    try:
        ytdlp = yt_dlp.YoutubeDL(mp4_opts)
        info = ytdlp.extract_info(link, download=True)
        rawfilename = ytdlp.prepare_filename(info)
        title = os.path.splitext(rawfilename)[0]
        filename = f"{title}.mp4"
        return filename
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def file_cleaner(path: str):
    os.remove(path)

@app.get("/download/mp3")
async def download_mp3(link: str, backgroundtask: BackgroundTasks):
    file = await run_in_threadpool(downloadpm3, link)
    backgroundtask.add_task(file_cleaner, file)

    return FileResponse(path=file, filename=os.path.basename(file))

@app.get("/download/mp4")
async def download_mp4(link: str, backgroundtask: BackgroundTasks):
    file = await run_in_threadpool(downloadmp4, link)
    backgroundtask.add_task(file_cleaner, file)

    return FileResponse(path=file, filename=os.path.basename(file))

@app.get("/health")
async def health():
    return {"health": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")