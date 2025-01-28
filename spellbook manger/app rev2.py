import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Create a database connection and table
conn = sqlite3.connect('spellbook.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS spells (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )
''')
conn.commit()

class SpellBookManager:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Harry Potter Spell Book")

        self.canvas = tk.Canvas(root, width=1000, height=300)
        self.canvas.pack()

        # Load and display the background image
        bg_image = Image.open("title.jpg")  # Replace with the path to your background image
        bg_image = bg_image.resize((1000, 300))  # Resize the background image to match the window size
        self.bg_photo = ImageTk.PhotoImage(image=bg_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)
        
        # Apply Harry Potter theme
        self.root.configure(bg='black')
        self.root.option_add('*TButton*background', 'goldenrod')
        self.root.option_add('*TButton*foreground', 'black')
        
        self.name_label = tk.Label(root, text="Spell Name:", bg='black', fg='white', font=('Helvetica', 12, 'bold'))
        self.name_label.pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack()
        
        self.desc_label = tk.Label(root, text="Spell Description:", bg='black', fg='white', font=('Helvetica', 12, 'bold'))
        self.desc_label.pack()
        self.desc_entry = tk.Entry(root)
        self.desc_entry.pack()
        
        self.add_button = tk.Button(root, text="Add Spell", command=self.add_spell)
        self.add_button.pack()
        
        self.spell_listbox = tk.Listbox(root, bg='black', fg='white', font=('Helvetica', 12))
        self.spell_listbox.pack()
        self.spell_listbox.bind('<<ListboxSelect>>', self.on_spell_selected)
        
        self.info_label = tk.Label(root, text="Spell Info:", bg='black', fg='white', font=('Helvetica', 12, 'bold'))
        self.info_label.pack()
        self.selected_spell_info = tk.StringVar()
        self.selected_spell_label = tk.Label(root, textvariable=self.selected_spell_info, bg='black', fg='white', font=('Helvetica', 12))
        self.selected_spell_label.pack()

        self.modify_button = tk.Button(root, text="Modify Spell", command=self.open_modify_window)
        self.modify_button.pack()

        self.delete_button = tk.Button(root, text="Delete Spell", command=self.delete_spell)
        self.delete_button.pack()

        
        self.load_spells()
    
    def add_spell(self):
        name = self.name_entry.get()
        description = self.desc_entry.get()
        
        if name and description:
            cursor.execute('INSERT INTO spells (name, description) VALUES (?, ?)', (name, description))
            conn.commit()
            
            self.name_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            
            self.load_spells()
        else:
            messagebox.showwarning("Warning", "Both name and description are required.")
    
    def load_spells(self):
        self.spell_listbox.delete(0, tk.END)
        cursor.execute('SELECT id, name FROM spells')
        spells = cursor.fetchall()
        for spell in spells:
            self.spell_listbox.insert(tk.END, f"{spell[0]}. {spell[1]}")

    def open_modify_window(self):
        selected_item_index = self.spell_listbox.curselection()
        if selected_item_index:
            selected_item_index = selected_item_index[0]
            selected_spell_id = self.spell_listbox.get(selected_item_index).split('.')[0]
            
            cursor.execute('SELECT name, description FROM spells WHERE id = ?', (selected_spell_id,))
            spell_info = cursor.fetchone()
            
            if spell_info:
                modify_window = tk.Toplevel(self.root)
                modify_window.title("Modify Spell")
                
                name_label = tk.Label(modify_window, text="Spell Name:", font=('Helvetica', 12, 'bold'))
                name_label.pack()
                name_entry = tk.Entry(modify_window)
                name_entry.insert(0, spell_info[0])
                name_entry.pack()
                
                desc_label = tk.Label(modify_window, text="Spell Description:", font=('Helvetica', 12, 'bold'))
                desc_label.pack()
                desc_entry = tk.Entry(modify_window)
                desc_entry.insert(0, spell_info[1])
                desc_entry.pack()
                
                update_button = tk.Button(modify_window, text="Update", command=lambda: self.update_spell(selected_spell_id, name_entry.get(), desc_entry.get(), modify_window))
                update_button.pack()
            else:
                messagebox.showwarning("Warning", "No spell selected")
        else:
            messagebox.showwarning("Warning", "Please select a spell to modify.")

    def update_spell(self, spell_id, new_name, new_description, modify_window):
        if new_name and new_description:
            cursor.execute('UPDATE spells SET name = ?, description = ? WHERE id = ?', (new_name, new_description, spell_id))
            conn.commit()
            modify_window.destroy()
            self.load_spells()
            self.selected_spell_info.set(f"Name: {new_name}\nDescription: {new_description}")
        else:
            messagebox.showwarning("Warning", "Both name and description are required for modification.")

    def delete_spell(self):
        selected_item_index = self.spell_listbox.curselection()
        if selected_item_index:
            selected_item_index = selected_item_index[0]
            selected_spell_id = self.spell_listbox.get(selected_item_index).split('.')[0]
            
            result = messagebox.askyesno("Confirmation", "Are you sure you want to delete this spell?")
            if result:
                cursor.execute('DELETE FROM spells WHERE id = ?', (selected_spell_id,))
                conn.commit()
                self.load_spells()
                self.selected_spell_info.set("No spell selected")
        else:
            messagebox.showwarning("Warning", "Please select a spell to delete.")
    
    def on_spell_selected(self, event):
        selected_item_index = self.spell_listbox.curselection()
        if selected_item_index:
            selected_item_index = selected_item_index[0]
            selected_spell_id = self.spell_listbox.get(selected_item_index).split('.')[0]
            
            cursor.execute('SELECT name, description FROM spells WHERE id = ?', (selected_spell_id,))
            spell_info = cursor.fetchone()
            if spell_info:
                self.selected_spell_info.set(f"Name: {spell_info[0]}\nDescription: {spell_info[1]}")
            else:
                self.selected_spell_info.set("No spell selected")
        else:
            self.selected_spell_info.set("No spell selected")

root = tk.Tk()
app = SpellBookManager(root)
root.mainloop()

conn.close()
