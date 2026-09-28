from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import yt_dlp
import os
from starlette.concurrency import run_in_threadpool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

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

def downloadpm3(link: str):
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

if __name__ == "__main__":
    uvicorn.run(app)