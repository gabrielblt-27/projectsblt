import sys
import subprocess
import os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QRadioButton,
    QProgressBar,
    QLabel,
)

from PySide6.QtCore import QProcess

def obter_duracao(arquivo):
    resultado = subprocess.run([
        'ffmpeg.exe',
        '-i',
        arquivo
    ], capture_output=True, text=True)

    texto = resultado.stderr

    inicio = texto.find('Duration: ')

    if inicio == -1:
        return 0

    duracao = texto[inicio + 10:inicio + 21]



    horas = int(duracao[0:2])
    minutos = int(duracao[3:5])
    segundos = float(duracao[6:])

    return (
        horas * 3600
        + minutos * 60
        + segundos
    )

def selecionar_arquivo():
    arquivo, _ = QFileDialog.getOpenFileName(
        janela,
        "Selecionar arquivo",
        "",
        "Arquivos de mídia (*.mp4 *.mp3)"
    )

    if arquivo:
        campo_arquivo.setText(arquivo)

def converter():

    global duracao_total

    arquivo = campo_arquivo.text()

    if not arquivo:
        print('Nenhum arquivo foi selecionado')
        return

    duracao_total = obter_duracao(arquivo)

    if mp3.isChecked():
        print('Arquivo MP4 selecionado para MP3')
        progresso.setValue(0)

        nome_original = os.path.splitext(os.path.basename(arquivo))[0]

        arquivo_saida, _ = QFileDialog.getSaveFileName(
            janela,
            'Salvar arquivo mp3',
            nome_original + '.mp3',
            'Arquivos MP3 (*.mp3)'
        )

        if not arquivo_saida:
            print('Salvamento cancelado')
            return

        processo.start(
            r'ffmpeg.exe',
            [
                '-i',
                arquivo,
                '-progress',
                'pipe:1',
                '-nostats',
                arquivo_saida
            ]
        )

    #   progresso.setValue(100)
    #  status.setText('Conversão Concluida!')

def atualizar_progresso():

    texto = processo.readAllStandardOutput().data().decode(
    'utf-8',
             errors='ignore')
    print(texto)

    for linha in texto.splitlines():
        if linha.startswith('out_time_ms='):

            tempo_atual = int(
                linha.split('=')[1]
            ) / 1_000_000

            if duracao_total > 0:

                porcentagem = int(
                    (tempo_atual / duracao_total) * 100
                )

                progresso.setValue(porcentagem)
                status.setText(
                    f'Convertendo... {porcentagem}%'
                )



def conversao_finalizada(exit_code, exit_status):
    if exit_code == 0:
        progresso.setValue(100)
        status.setText('Conversão Finalizada!')
        print('Conversão Concluida!')

    else:
        status.setText('Erro na Conversão')
        print('Ocorreu um erro na conversão')


app = QApplication(sys.argv)

processo = QProcess()
duracao_total = 0
processo.readyReadStandardOutput.connect(atualizar_progresso)
processo.finished.connect(conversao_finalizada)

janela = QWidget()

janela.setWindowTitle("Conversor de Mídia")
janela.resize(500, 300)

status = QLabel('Aguardando arquivo',janela)
status.move(30, 260)

progresso = QProgressBar(janela)
progresso.move(30, 285)
progresso.resize(440, 25)
progresso.setValue(0)

campo_arquivo = QLineEdit(janela)
campo_arquivo.setPlaceholderText("Nenhum arquivo selecionado")
campo_arquivo.move(30, 70)
campo_arquivo.resize(440, 30)
mp3 = QRadioButton('MP3',janela)
mp3.move(150, 170)
mp3.setChecked(True)

botao_converter = QPushButton("Converter", janela)
botao_converter.move(190, 220)
botao_converter.clicked.connect(converter)

botao = QPushButton("Selecionar arquivo", janela)
botao.move(170, 120)

botao.clicked.connect(selecionar_arquivo)

janela.show()

sys.exit(app.exec())