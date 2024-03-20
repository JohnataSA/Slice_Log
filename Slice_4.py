import os
import time  # Adicione esta linha para importar o módulo time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MonitorHandler(FileSystemEventHandler):
    def process(self, event):
        """Processa o arquivo criado ou modificado."""
        if event.is_directory or not event.src_path.endswith('.txt'):
            return
        print(f"Processando arquivo: {event.src_path}")
        try:
            with open(event.src_path, 'r') as arquivo:
                ultima_posicao = 0  # Presume-se começar do início para novos arquivos
                self.recortar_logs(arquivo, ultima_posicao)
        except Exception as e:
            print(f"Erro ao processar arquivo {event.src_path}: {e}")

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def recortar_logs(self, arquivo, ultima_posicao):
        arquivo.seek(ultima_posicao)
        novas_linhas = arquivo.readlines()
        conteudo = ''.join(novas_linhas)

        indices_inicio = []
        indices_fim = []

        indice_inicio = conteudo.find("SN:Y")
        while indice_inicio != -1:
            indices_inicio.append(indice_inicio)
            indice_fim = conteudo.find("End  ==================== Inspection End OK ====================",
                                       indice_inicio)
            if indice_fim != -1:
                indices_fim.append(indice_fim + len("End  ==================== Inspection End OK ===================="))
            else:
                indices_fim.append(len(conteudo))
                break
            indice_inicio = conteudo.find("SN:Y", indice_fim)

        pasta_destino = r"C:/MGASPEC/Buff"
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        for inicio, fim in zip(indices_inicio, indices_fim):
            serial = conteudo[inicio + 3:inicio + 18]  # Ajuste para incluir o último caractere
            log = conteudo[inicio:fim]
            nome_arquivo_novo = os.path.join(pasta_destino, f"{serial}.txt")
            with open(nome_arquivo_novo, 'w') as arquivo_novo:
                arquivo_novo.write(log)


if __name__ == "__main__":
    path_to_watch = "C:/MGASPEC/Test/Renaissance_Log"
    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()

    print("Monitorando mudanças. Pressione Ctrl+C para sair.")
    try:
        while True:
            time.sleep(1)  # Adiciona isso para evitar uso intenso da CPU
    except KeyboardInterrupt:
        observer.stop()
    observer.join()