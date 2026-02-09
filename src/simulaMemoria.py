import tkinter as tk
from tkinter import messagebox, ttk

class MemoryBlock:
    def __init__(self, start, size):
        self.start = start
        self.size = size

class MemoryManager:
    def __init__(self, total_size):
        self.total_size = total_size
        self.free_blocks = [MemoryBlock(0, total_size)]
        self.allocated_blocks = []
        self.next_fit_index = 0
        self.last_allocated_start = 0

    def allocate(self, size, strategy):
        if strategy == "First Fit":
            return self.allocate_first_fit(size)
        elif strategy == "Best Fit":
            return self.allocate_best_fit(size)
        elif strategy == "Worst Fit":
            return self.allocate_worst_fit(size)
        elif strategy == "Next Fit":
            return self.allocate_next_fit(size)

    def allocate_first_fit(self, size):
        for i, block in enumerate(self.free_blocks):
            if block.size >= size:
                allocated_start = block.start
                self.allocated_blocks.append(MemoryBlock(allocated_start, size))
                block.start += size
                block.size -= size
                if block.size == 0:
                    self.free_blocks.pop(i)
                return allocated_start
        return None

    def allocate_best_fit(self, size):
        best_index = -1
        best_size = float('inf')
        for i, block in enumerate(self.free_blocks):
            if block.size >= size and block.size < best_size:
                best_index = i
                best_size = block.size
        if best_index != -1:
            block = self.free_blocks[best_index]
            allocated_start = block.start
            self.allocated_blocks.append(MemoryBlock(allocated_start, size))
            block.start += size
            block.size -= size
            if block.size == 0:
                self.free_blocks.pop(best_index)
            return allocated_start
        return None

    def allocate_worst_fit(self, size):
        worst_index = -1
        worst_size = -1
        for i, block in enumerate(self.free_blocks):
            if block.size >= size and block.size > worst_size:
                worst_index = i
                worst_size = block.size
        if worst_index != -1:
            block = self.free_blocks[worst_index]
            allocated_start = block.start
            self.allocated_blocks.append(MemoryBlock(allocated_start, size))
            block.start += size
            block.size -= size
            if block.size == 0:
                self.free_blocks.pop(worst_index)
            return allocated_start
        return None

    def allocate_next_fit(self, size):
        n = len(self.free_blocks)
        if n == 0:
            return None

        i = self.next_fit_index % n
        start_index = i

        while True:
            if i >= len(self.free_blocks):
                i = 0

            block = self.free_blocks[i]
            if block.size >= size:
                allocated_start = block.start
                self.allocated_blocks.append(MemoryBlock(allocated_start, size))
                block.start += size
                block.size -= size
                if block.size == 0:
                    self.free_blocks.pop(i)
                    if i < self.next_fit_index:
                        self.next_fit_index -= 1
                    self.next_fit_index = i % len(self.free_blocks) if self.free_blocks else 0
                else:
                    self.next_fit_index = i
                self.last_allocated_start = allocated_start
                return allocated_start
            i = (i + 1) % n
            if i == start_index:
                break
        return None

    def free(self, address, size):
        for block in self.allocated_blocks:
            if block.start == address and block.size == size:
                self.allocated_blocks.remove(block)
                self.free_blocks.append(MemoryBlock(address, size))
                self.merge_blocks()
                return True
        return False

    def merge_blocks(self):
        self.free_blocks.sort(key=lambda b: b.start)
        merged = []
        for block in self.free_blocks:
            if not merged:
                merged.append(block)
            else:
                last = merged[-1]
                if last.start + last.size == block.start:
                    last.size += block.size
                else:
                    merged.append(block)
        self.free_blocks = merged

        self.next_fit_index = self.find_index_by_start(self.last_allocated_start)
        if self.next_fit_index >= len(self.free_blocks):
            self.next_fit_index = 0

    def find_index_by_start(self, start):
        for i, block in enumerate(self.free_blocks):
            if block.start >= start:
                return i
        return 0

    def get_state(self):
        state = []
        for block in self.free_blocks:
            state.append(f"Livre -> Início: {block.start}, Tamanho: {block.size}")
        for block in self.allocated_blocks:
            state.append(f"Alocado -> Início: {block.start}, Tamanho: {block.size}")
        return state

class MemoryManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Gerenciador de Memoria")

        self.manager = MemoryManager(100)

        self.strategy_var = tk.StringVar(value="First Fit")
        self.strategy_menu = ttk.Combobox(master, textvariable=self.strategy_var, values=["First Fit", "Best Fit", "Worst Fit", "Next Fit"])
        self.strategy_menu.pack(pady=5)

        self.allocate_frame = tk.Frame(master)
        self.allocate_frame.pack(pady=5)

        tk.Label(self.allocate_frame, text="Tamanho a alocar:").grid(row=0, column=0)
        self.alloc_entry = tk.Entry(self.allocate_frame, width=5)
        self.alloc_entry.grid(row=0, column=1, padx=5)
        tk.Button(self.allocate_frame, text="Alocar", command=self.allocate_memory).grid(row=0, column=2, padx=5)

        self.free_frame = tk.Frame(master)
        self.free_frame.pack(pady=5)

        tk.Label(self.free_frame, text="Endereco:").grid(row=0, column=0)
        self.free_addr_entry = tk.Entry(self.free_frame, width=5)
        self.free_addr_entry.grid(row=0, column=1, padx=5)
        tk.Label(self.free_frame, text="Tamanho:").grid(row=0, column=2)
        self.free_size_entry = tk.Entry(self.free_frame, width=5)
        self.free_size_entry.grid(row=0, column=3, padx=5)
        tk.Button(self.free_frame, text="Liberar", command=self.free_memory).grid(row=0, column=4, padx=5)

        self.state_listbox = tk.Listbox(master, width=50)
        self.state_listbox.pack(pady=10)

         # para visualização dos blocos de memória
        self.canvas = tk.Canvas(master, width=500, height=100, bg="white")
        self.canvas.pack(pady=10)


        self.update_state() # isso aqui atualiza o estado da tela

    def allocate_memory(self):
        size_str = self.alloc_entry.get().strip()
        if size_str:
            try:
                size = int(size_str)
                if size <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Tamanho deve ser inteiro")
                return
            strategy = self.strategy_var.get()
            addr = self.manager.allocate(size, strategy)
            if addr is not None:
                messagebox.showinfo("Alocado", f"Memoria alocada a partir do endereco {addr}")
            else:
                messagebox.showwarning("Insuficiente", "Memoria insuficiente")
            self.alloc_entry.delete(0, tk.END)
            self.update_state()

    def free_memory(self):
        addr_str = self.free_addr_entry.get().strip()
        size_str = self.free_size_entry.get().strip()
        if addr_str and size_str:
            try:
                addr = int(addr_str)
                size = int(size_str)
                if addr < 0 or size <= 0 or addr + size > self.manager.total_size:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Endereco e tamanho devem ser inteiros")
                return
            success = self.manager.free(addr, size)
            if success:
                messagebox.showinfo("Liberado", f"Liberadas {size} unidades no endereco {addr}")
            else:
                messagebox.showerror("Erro", f"Bloco não está alocado em {addr} com tamanho {size}")
            self.free_addr_entry.delete(0, tk.END)
            self.free_size_entry.delete(0, tk.END)
            self.update_state()
        else:
            messagebox.showwarning("Aviso", "Preencha endereco e tamanho")

    def update_state(self):
        # Atualiza a ListBox com o estado textual dos blocos
        self.state_listbox.delete(0, tk.END)
        for state in self.manager.get_state():
            self.state_listbox.insert(tk.END, state)
        # Atualiza a visualização gráfica
        self.draw_memory()


    def draw_memory(self):
        # Criando a interface para mostrar as regiões alocadas de forma melhor.
        self.canvas.delete("all")
        total = self.manager.total_size
        canvas_width = int(self.canvas['width'])
        canvas_height = int(self.canvas['height'])
        scale = canvas_width / total

        # Cria uma lista de blocos: cada item é uma tupla (início, tamanho, cor)
        # Blocos alocados em vermelho e blocos livres em verde
        blocks = []
        for block in self.manager.allocated_blocks:
            blocks.append((block.start, block.size, "red"))
        for block in self.manager.free_blocks:
            blocks.append((block.start, block.size, "green"))

        # Ordena os blocos pelo endereço inicial
        blocks.sort(key=lambda x: x[0])

        # Desenha cada bloco
        for (start, size, color) in blocks:
            x1 = start * scale
            x2 = (start + size) * scale
            self.canvas.create_rectangle(x1, 10, x2, canvas_height - 10, fill=color)
            self.canvas.create_text((x1+x2)/2, canvas_height/2, text=f"{size}", fill="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagerApp(root)
    root.mainloop()
