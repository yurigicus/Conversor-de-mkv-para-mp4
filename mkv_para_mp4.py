from pathlib import Path
import subprocess
import re

pasta = Path(__file__).parent

arquivos = list(pasta.glob("*.mkv"))

if not arquivos:
    print("Nenhum arquivo MKV encontrado na pasta do script.")
    input("\nPressione Enter para sair...")
    exit()

for arquivo in arquivos:
    saida = arquivo.with_suffix(".mp4")

    print(f"\nConvertendo: {arquivo.name}")

    # duração do vídeo
    resultado = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(arquivo)
        ],
        capture_output=True,
        text=True
    )

    duracao_total = float(resultado.stdout.strip())

    comando = [
        "ffmpeg",
        "-y",
        "-i", str(arquivo),

        # vídeo
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",

        # compatibilidade
        "-movflags", "+faststart",

        # áudio
        "-c:a", "aac",
        "-b:a", "192k",

        str(saida)
    ]

    processo = subprocess.Popen(
        comando,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    regex_tempo = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    regex_speed = re.compile(r"speed=\s*([\d\.]+)x")

    speed_atual = "?"

    for linha in processo.stderr:

        match_speed = regex_speed.search(linha)
        if match_speed:
            speed_atual = match_speed.group(1)

        match_tempo = regex_tempo.search(linha)
        if match_tempo:
            h, m, s = match_tempo.groups()

            tempo_atual = (
                int(h) * 3600 +
                int(m) * 60 +
                float(s)
            )

            porcentagem = min(
                (tempo_atual / duracao_total) * 100,
                100
            )

            print(
                f"\r{arquivo.name} | "
                f"{porcentagem:6.2f}% | "
                f"speed={speed_atual}x",
                end="",
                flush=True
            )

    processo.wait()

    if processo.returncode == 0:

        tamanho_original = arquivo.stat().st_size / (1024**3)
        tamanho_final = saida.stat().st_size / (1024**3)

        arquivo.unlink()

        print("\r" + " " * 120, end="")
        print(
            f"\rConcluído: {saida.name} | "
            f"{tamanho_original:.2f} GB → {tamanho_final:.2f} GB"
        )

    else:
        print(f"\nErro ao converter {arquivo.name}")

print("\nTodas as conversões foram concluídas.")
input("\nPressione Enter para sair...")