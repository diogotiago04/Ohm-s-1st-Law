import tkinter as tk
from tkinter import messagebox
import serial
import time
import matplotlib.pyplot as plt

class OhmInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificação experimental da 1ª Lei de Ohm")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        self.arduino = None
        self.conectado = False
        self.dados_dict = {}
        self.medida_atual = None

        tk.Label(root, text="Verificação experimental da 1ª Lei de Ohm",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(20, 5))
        tk.Frame(root, height=1, bg="gray").pack(fill="x", padx=40, pady=10)

        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(pady=10)

        coluna_esq = tk.Frame(main_frame, bg="#f0f0f0")
        coluna_esq.grid(row=0, column=0, padx=30)

        tk.Label(coluna_esq, text="Porta Serial (ex: COM3):", bg="#f0f0f0").pack()
        self.entrada_porta = tk.Entry(coluna_esq, width=20, justify="center")
        self.entrada_porta.pack(pady=5)

        self.botao_conectar = tk.Button(coluna_esq, text="Conectar", width=15, command=self.toggle_conexao)
        self.botao_conectar.pack(pady=10)

        tk.Label(coluna_esq, text="Aplicar tensão no circuito (V):", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(15, 5))

        self.tensao_var = tk.DoubleVar()
        self.tensao_var.set(0.0)

        frame_radios = tk.Frame(coluna_esq, bg="#f0f0f0")
        frame_radios.pack()

        self.tensoes_possiveis = [float(v) for v in range(0, 6)]
        for i, valor in enumerate(self.tensoes_possiveis):
            tk.Radiobutton(frame_radios, text=f"{valor:.1f} V", variable=self.tensao_var,
                           value=valor, bg="#f0f0f0").grid(row=i, column=0, padx=10, pady=2, sticky="w")

        self.botao_aplicar = tk.Button(coluna_esq, text="Aplicar Tensão", width=15, command=self.enviar_tensao)
        self.botao_aplicar.pack(pady=10)

        self.coluna_dir = tk.Frame(main_frame, bg="#f0f0f0")
        self.coluna_dir.grid(row=0, column=1, padx=30)

        tk.Label(self.coluna_dir, text="Medida Realizada", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(5, 5))

        linha_tensao = tk.Frame(self.coluna_dir, bg="#f0f0f0")
        linha_tensao.pack(pady=2)
        tk.Label(linha_tensao, text="Tensão medida (V):", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.entry_tensao = tk.Entry(linha_tensao, width=12, justify="center", font=("Arial", 10), state="readonly")
        self.entry_tensao.grid(row=0, column=1)

        linha_corrente = tk.Frame(self.coluna_dir, bg="#f0f0f0")
        linha_corrente.pack(pady=2)
        tk.Label(linha_corrente, text="Corrente medida (mA):", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.entry_corrente = tk.Entry(linha_corrente, width=12, justify="center", font=("Arial", 10), state="readonly")
        self.entry_corrente.grid(row=0, column=1)

        linha_botoes = tk.Frame(self.coluna_dir, bg="#f0f0f0")
        linha_botoes.pack(pady=(10, 20))

        self.botao_exportar = tk.Button(linha_botoes, text="Confirmar Medida", command=self.exibir_medidas)
        self.botao_exportar.grid(row=0, column=0, padx=5)

        self.botao_cancelar = tk.Button(linha_botoes, text="Cancelar Medida", command=self.cancelar_medida)
        self.botao_cancelar.grid(row=0, column=1, padx=5)

        cabecalho = tk.Frame(self.coluna_dir, bg="#f0f0f0")
        cabecalho.pack()
        tk.Label(cabecalho, text="Tensão (V)", width=12, font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        tk.Label(cabecalho, text="Corrente (mA)", width=12, font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=1, padx=5)

        self.entradas_medidas = []
        for _ in range(6):
            linha = tk.Frame(self.coluna_dir, bg="#f0f0f0")
            linha.pack(pady=2)
            entrada_v = tk.Entry(linha, width=12, justify="center", state="readonly", font=("Arial", 10))
            entrada_v.grid(row=0, column=0, padx=5)
            entrada_i = tk.Entry(linha, width=12, justify="center", state="readonly", font=("Arial", 10))
            entrada_i.grid(row=0, column=1, padx=5)
            self.entradas_medidas.append((entrada_v, entrada_i))

        botoes_frame = tk.Frame(self.coluna_dir, bg="#f0f0f0")
        botoes_frame.pack(pady=(30, 10))

        self.btn_grafico = tk.Button(botoes_frame, text="Gráfico", width=10, command=self.plotar_grafico, state="disabled")
        self.btn_grafico.grid(row=0, column=0, padx=5)

        self.btn_resistor = tk.Button(botoes_frame, text="Resistor", width=10, command=self.calcular_resistor, state="disabled")
        self.btn_resistor.grid(row=0, column=1, padx=5)

        self.btn_iniciar = tk.Button(botoes_frame, text="Iniciar", width=10, command=self.reiniciar)
        self.btn_iniciar.grid(row=0, column=2, padx=5)

    def toggle_conexao(self):
        if not self.conectado:
            porta = self.entrada_porta.get()
            try:
                self.arduino = serial.Serial(porta, 9600, timeout=2)
                time.sleep(2)
                self.conectado = True
                self.botao_conectar.config(text="Desconectar")
                messagebox.showinfo("Conectado", f"Conectado à porta {porta}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na conexão: {e}")
        else:
            if self.arduino:
                self.arduino.close()
            self.conectado = False
            self.botao_conectar.config(text="Conectar")
            messagebox.showinfo("Desconectado", "Desconectado com sucesso.")

    def enviar_tensao(self):
        if self.conectado and self.arduino:
            tensao = self.tensao_var.get()
            pwm_valor = int(tensao * 51)
            comando = f"{pwm_valor}"
            self.arduino.write(comando.encode())
            time.sleep(1.5)

            try:
                v_rx = float(self.arduino.readline().decode().strip())
                corrente = float(self.arduino.readline().decode().strip())
                self.set_entry_value(self.entry_tensao, f"{v_rx:.2f}")
                self.set_entry_value(self.entry_corrente, f"{corrente:.1f}")
                self.medida_atual = (tensao, v_rx, corrente)
            except:
                messagebox.showerror("Erro", "Leitura inválida do Arduino.")
        else:
            messagebox.showwarning("Aviso", "Conecte-se ao Arduino primeiro.")

    def set_entry_value(self, entry, value):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.config(state="readonly")

    def exibir_medidas(self):
        if self.medida_atual is None:
            messagebox.showwarning("Aviso", "Nenhuma medição para exportar.")
            return

        tensao, v_rx, corrente = self.medida_atual
        self.dados_dict[tensao] = (v_rx, corrente)
        ordenadas = sorted(self.dados_dict.items())

        for i in range(6):
            if i < len(ordenadas):
                _, (vrx, i_mA) = ordenadas[i]
                self.set_entry_value(self.entradas_medidas[i][0], f"{vrx:.2f}")
                self.set_entry_value(self.entradas_medidas[i][1], f"{i_mA:.1f}")
            else:
                self.set_entry_value(self.entradas_medidas[i][0], "--")
                self.set_entry_value(self.entradas_medidas[i][1], "--")

        messagebox.showinfo("Exportação", "Medida exportada com sucesso. Pronto para nova medição.")
        self.set_entry_value(self.entry_tensao, "--")
        self.set_entry_value(self.entry_corrente, "--")
        self.medida_atual = None

        if len(self.dados_dict) >= 2:
            self.btn_grafico.config(state="normal")
            self.btn_resistor.config(state="normal")

    def cancelar_medida(self):
        self.set_entry_value(self.entry_tensao, "--")
        self.set_entry_value(self.entry_corrente, "--")
        self.medida_atual = None
        messagebox.showinfo("Cancelado", "Medição atual cancelada. Nenhum dado foi salvo.")

    def plotar_grafico(self):
        if len(self.dados_dict) >= 2:
            dados = sorted(self.dados_dict.items())
            tensoes = [vrx for _, (vrx, _) in dados]
            correntes = [i for _, (_, i) in dados]
            plt.figure("Curva V x I")
            plt.plot(correntes, tensoes, marker='o')
            plt.xlabel("Corrente (mA)")
            plt.ylabel("Tensão (V)")
            plt.title("Curva Característica V x I")
            plt.grid(True)
            plt.show()

    def calcular_resistor(self):
        if len(self.dados_dict) >= 2:
            dados = sorted(self.dados_dict.items())
            tensoes = [vrx for _, (vrx, _) in dados]
            correntes = [i for _, (_, i) in dados]
            try:
                coef = sum(v * (i / 1000) for v, i in zip(tensoes, correntes)) / sum((i / 1000) ** 2 for i in correntes)
                coef *= 1
                messagebox.showinfo("Resistor", f"De acordo com as medidas, o resistor é de {coef:.2f} Ohms.")
            except:
                messagebox.showerror("Erro", "Não foi possível calcular o resistor.")

    def reiniciar(self):
        self.dados_dict.clear()
        self.medida_atual = None
        self.set_entry_value(self.entry_tensao, "--")
        self.set_entry_value(self.entry_corrente, "--")
        for entrada_v, entrada_i in self.entradas_medidas:
            self.set_entry_value(entrada_v, "--")
            self.set_entry_value(entrada_i, "--")
        self.btn_grafico.config(state="disabled")
        self.btn_resistor.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = OhmInterface(root)
    root.mainloop()
