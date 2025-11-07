import psycopg2
import tkinter as tk
from tkinter import messagebox
from datetime import date
from datetime import datetime
import sys

#INICIO ABERTURA DE ARQUIVO CONFIGURAÇÃO
try:
     with open("cfg.txt", "r") as arquivo:
        config = arquivo.readlines()
except Exception as erro:
    messagebox.showerror('Mensagem de erro!', erro)
else:
    host = config[0].strip()      #IP do servidor
    port = config[1].strip()             #porta
    database = config[2].strip()       #nome db
    user = config[3].strip()       #usuário postgresql
    password = config[4].strip()     #senha postgresql
#FINAL ABERTURA DE ARQUIVO CONFIGURAÇÃO

def banco():
     try:
          global cursor
          global conexao
          conexao = psycopg2.connect(
           host=host,
           port=port,
           database=database,
           user=user,
           password=password)
          cursor = conexao.cursor()
     except Exception as erro:
          messagebox.showerror('Mensagem de erro!', erro)
          sys.exit()
     else:
          cursor.close
          conexao.close 

# inicio - Pegando versão do postgresql 
banco()           
cursor.execute("SELECT version();")
versao = cursor.fetchone()
#fim - pegando versão do postgresql

banco()
cursor.execute("SELECT datavigenciafinal FROM ncm")
vigencia = cursor.fetchall()
data_atual = date.today()
data_atual = str(data_atual).strip()
data_atual_formatada = datetime.strptime(data_atual, "%Y-%m-%d").date()
erro = 0

for x in vigencia:
     x = str(x).replace('(','').replace(')','').replace('.','').replace(',','').replace('datetimedate','').replace(' ','-').strip()
     data_banco_formatada = datetime.strptime(x, "%Y-%m-%d").date()
     if data_atual_formatada > data_banco_formatada:
          erro+=1

if erro == 0:
     messagebox.showinfo(message = f"""TABELA IBPT VÁLIDA! \nVIGÊNCIA LIMITE: {data_banco_formatada} \nDATA ATUAL: {data_atual_formatada}""")
else:
     messagebox.showerror(message = f"""TABELA IBPT VENCIDA! \nVIGÊNCIA LIMITE: {data_banco_formatada} \nDATA ATUAL: {data_atual_formatada}""")
     sys.exit()

# Criando a janela principal
janela = tk.Tk()
janela.title("BNI 1.3")
janela.geometry("700x500")  # Largura x Altura

#label do texto versao postgresql
label = tk.Label(janela, text=versao)
label.pack(pady=10)

# campo grande onde fica o resultado query
campo_query = tk.Text(janela, width=80, height=10,bg="lightblue",fg="white",state="disabled")
campo_query.pack(pady=5)

def valid():
     campo_query.config(state='normal') 
     campo_query.delete("1.0",tk.END)
     campo_query.config(state='disabled') 
     banco()   
     cursor.execute("""SELECT 
     COUNT(*)
     FROM 
     produto p
     LEFT JOIN 
     ncm n ON p.ncm = n.idncm
     WHERE 
     n.idncm IS NULL;""")
     query2 = cursor.fetchall()  
     query2 = str(query2).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","") 
     query2 = int(query2)
     if query2 == 0:
          campo_query.config(state='normal')  
          campo_query.insert(tk.END, 'Não foram encontrados itens com NCM inválido!')
          campo_query.config(state='disabled')  

     else:
          cursor.execute("""SELECT 
          p.idproduto,
          p.descricaoproduto,
          p.ncm 
          FROM 
          produto p
          LEFT JOIN 
          ncm n ON p.ncm = n.idncm
          WHERE 
          n.idncm IS NULL;""")
          query = cursor.fetchall()
          campo_query.config(state='normal')  
          campo_query.delete("1.0",tk.END)
          campo_query.insert(tk.END, f'Itens encontrados: {query2}' + "\n" + "\n")     
          for x in query:
               x = str(x).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")
               campo_query.insert(tk.END, str(x) + "\n")

          campo_query.config(state='disabled')   

def apagar():
     campo_query.config(state='normal')   
     campo_query.delete("1.0",tk.END)
     campo_query.config(state='disabled')  

def atualizar():
     banco()
     resposta = messagebox.askyesno('Confirmação', f"Atualizar todos os itens com ncm inválido para o ncm genérico '00000000' ?")
     if resposta:
          cursor.execute("""UPDATE produto p
SET ncm = '00000000'
WHERE NOT EXISTS (
    SELECT 1 FROM ncm n WHERE n.idncm = p.ncm
);""")
          conexao.commit()
          messagebox.showinfo('Informação', f'Operação realizada com sucesso!')  
          campo_query.config(state='normal')   
          campo_query.delete("1.0",tk.END)
          campo_query.config(state='disabled')  
     else:
          messagebox.showinfo('Informação', 'Operação cancelada!')     
     
# botão de buscar, apagar, atualizar
botao = tk.Button(janela, text="buscar", command=valid,bg='green',fg='white')
botao.pack(pady=10)
botao = tk.Button(janela, text="apagar", command=apagar,bg='red',fg='white')
botao.pack(pady=10)
botao = tk.Button(janela, text="atualizar", command=atualizar,bg='blue',fg='white')
botao.pack(pady=10)

# Iniciando o loop da interface
janela.mainloop()
