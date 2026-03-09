import glob
import os
import sys
from pydub import AudioSegment
import yt_dlp


def newest_mp3_filename():
    list_of_mp3s = glob.glob("./*.mp3")
    if not list_of_mp3s:
        return None
    return max(list_of_mp3s, key=os.path.getctime)


def get_video_time_in_ms(video_timestamp: str) -> int:
    vt_split = video_timestamp.split(":")
    if len(vt_split) == 3:  # HH:MM:SS
        hours = int(vt_split[0]) * 60 * 60 * 1000
        minutes = int(vt_split[1]) * 60 * 1000
        seconds = int(vt_split[2]) * 1000
    elif len(vt_split) == 2:  # MM:SS
        hours = 0
        minutes = int(vt_split[0]) * 60 * 1000
        seconds = int(vt_split[1]) * 1000
    else:
        raise ValueError(f"Timestamp inválido: {video_timestamp}")

    return hours + minutes + seconds


def get_trimmed(mp3_filename, initial, final=""):
    if not mp3_filename:
        raise Exception("No se encontró ningún MP3 en el directorio local.")

    sound = AudioSegment.from_mp3(mp3_filename)
    t0 = get_video_time_in_ms(initial)

    print(f"Comenzando proceso de recorte para {mp3_filename}")
    print(f"Comenzando desde {initial}...")

    if final:
        print(f"...hasta {final}.")
        t1 = get_video_time_in_ms(final)
        return sound[t0:t1]

    return sound[t0:]


def download_audio(yt_url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "noplaylist": True,
        "verbose": True,  # útil para depurar
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <URL> [inicio] [fin]")
        return

    yt_url = sys.argv[1]
    download_audio(yt_url)

    # Si no hay recorte, termina tras descargar
    if len(sys.argv) < 3:
        return

    initial = sys.argv[2]
    final = sys.argv[3] if len(sys.argv) > 3 else ""

    filename = newest_mp3_filename()
    trimmed_file = get_trimmed(filename, initial, final)

    trimmed_filename = filename.replace(".mp3", "-TRIM.mp3")
    print(f"El proceso finalizó con éxito. Guardando archivo como {trimmed_filename}")
    trimmed_file.export(trimmed_filename, format="mp3")


if __name__ == "__main__":
    main()