import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os


class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("My Game Box 🎮")
        self.root.geometry("500x400")

        # 设置一个美观的样式
        self.setup_style()

        # 游戏列表数据： (显示名, 对应的游戏模块类名)
        self.games = [
            ("🐍 Snake Game", "snake_game.SnakeGame"),
            ("⭕ Tic-Tac-Toe", "tic_tac_toe.TicTacToe"),
            #("👻 Pac-Man", "pacman_game.PacManGame"),有bug
            ("🔷 Tetris", "tetris_game.TetrisGame"),
            ("✈️ Air Battle", "plane_shooter_simple.PlaneShooter"),
            ("💣 Minesweeper", "minesweeper_game.Minesweeper"),
            # 未来可以在这里添加更多游戏：
        ]

        self.create_widgets()

    def setup_style(self):
        """设置窗口和部件的样式"""
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg='#2E3440')

    def create_widgets(self):
        """创建启动器界面的所有部件"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="Welcome to Game Box",
            font=('Arial', 24, 'bold'),
            fg='#88C0D0',
            bg='#2E3440'
        )
        title_label.pack(pady=(30, 10))

        # 副标题
        subtitle_label = tk.Label(
            self.root,
            text="Select a game to play:",
            font=('Arial', 12),
            fg='#D8DEE9',
            bg='#2E3440'
        )
        subtitle_label.pack(pady=(0, 20))

        # 创建列表框架
        list_frame = tk.Frame(self.root, bg='#3B4252')
        list_frame.pack(pady=10, padx=50, fill=tk.BOTH, expand=True)

        # 游戏列表
        self.game_listbox = tk.Listbox(
            list_frame,
            height=6,
            font=('Arial', 12),
            bg='#434C5E',
            fg='#E5E9F0',
            selectbackground='#5E81AC',
            selectforeground='white',
            activestyle='none',
            borderwidth=0,
            highlightthickness=0
        )

        # 向列表中添加游戏
        for game_name, _ in self.games:
            self.game_listbox.insert(tk.END, game_name)

        # 默认选择第一个游戏
        self.game_listbox.selection_set(0)

        # 添加滚动条
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.game_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.game_listbox.yview)

        # 布局
        self.game_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        button_frame = tk.Frame(self.root, bg='#2E3440')
        button_frame.pack(pady=30)

        # 播放按钮
        play_btn = tk.Button(
            button_frame,
            text="▶  Play Game",
            command=self.launch_game,
            font=('Arial', 12, 'bold'),
            bg='#5E81AC',
            fg='white',
            activebackground='#81A1C1',
            activeforeground='white',
            padx=30,
            pady=10,
            borderwidth=0,
            cursor='hand2'
        )
        play_btn.pack(side=tk.LEFT, padx=10)

        # 退出按钮
        quit_btn = tk.Button(
            button_frame,
            text="❌  Exit",
            command=self.root.quit,
            font=('Arial', 12),
            bg='#BF616A',
            fg='white',
            activebackground='#D08770',
            activeforeground='white',
            padx=30,
            pady=10,
            borderwidth=0,
            cursor='hand2'
        )
        quit_btn.pack(side=tk.LEFT, padx=10)

        # 绑定双击事件和回车键
        self.game_listbox.bind('<Double-Button-1>', lambda e: self.launch_game())
        self.root.bind('<Return>', lambda e: self.launch_game())

    def launch_game(self):
        """启动选中的游戏"""
        selection = self.game_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a game first!")
            return

        game_index = selection[0]
        game_module_class = self.games[game_index][1]

        # 隐藏启动器窗口
        self.root.withdraw()

        try:
            # 动态导入游戏模块并运行
            module_name, class_name = game_module_class.split('.')
            module = __import__(module_name)
            game_class = getattr(module, class_name)

            # 运行游戏
            game_instance = game_class()
            game_instance.run()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch game:\n{str(e)}")
            print(f"Error details: {e}")

        # 游戏结束后，重新显示启动器
        self.root.deiconify()


def main():
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()