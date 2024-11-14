import discord
from discord import app_commands
import json
import os
import random
from datetime import datetime, timedelta
from discord import Interaction
import pytz

id_do_servidor = 
DATA_FILE = 'accounts_data.json'
JOBS_FILE = 'jobs_data.json'
TIMEZONE = pytz.timezone("America/Sao_Paulo")

job_slots = {
    "Café da Sarah": 4, "Grillby's": 6, "Bliblioteca": 6, "Neko Café": 3,
    "Muffet": 8, "Hospital (superfície)": 6, "Hospital (Ômega Timeline)": 6,
    "Hotel (Snowdin)": 2, "Hotel (MTT)": 2, "Hotel (Superfície)": 3,
    "Restaurante do Grillby's": 2, "Restaurante ômega": 2, "Mercado MTT": 2,
    "Shopping": 6, "Secretária, professor e tia da merenda": 6, "Clownn's": 6
}

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.accounts = self.load_data(DATA_FILE)
        self.jobs = self.load_data(JOBS_FILE, default={job: 0 for job in job_slots})

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Logged in as {self.user}.")
    
    def load_data(self, filename, default=None):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return json.load(file)
        return default if default is not None else {}

    def save_data(self, filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file)

    def save_accounts(self):
        self.save_data(DATA_FILE, self.accounts)

    async def custom_close(self):
        self.save_accounts()
        self.save_data(JOBS_FILE, self.jobs)
        await super().close()

    async def has_required_role(self, interaction: discord.Interaction) -> bool:
        """Check if the user has the required role."""
        if interaction.guild is None:
            return False  # If no guild, user can't have the required role

        # Replace "RequiredRoleName" with the actual role name
        required_role = discord.utils.get(interaction.guild.roles, name="RequiredRoleName")
        if required_role is None:
            return False  # If the role doesn’t exist, deny access

        # Ensure that interaction.user is a Member to access roles
        if isinstance(interaction.user, discord.Member):
            return required_role in interaction.user.roles

        return False

def generate_job_message():
    job_message = "> ***```Atualizações dos trabalhos:```***\n> \n"
    for job, max_slots in job_slots.items():
        claimed_slots = aclient.jobs.get(job, 0)
        job_message += f"> ***```— {job} ({claimed_slots}/{max_slots})```***\n"
    job_message += (
        "> \n"
        "> ***```As vagas desses locais são limitadas, mas podem aumentar com o tempo.```***\n"
        "> ***```Lembra-se! Esses trabalhos são por PERSONAGEM e não por autor. "
        "Assim como o dinheiro, cada personagem tem que ter sua própria conta bancária no BANCO.```***"
    )
    return job_message

aclient = Client()
tree = app_commands.CommandTree(aclient)

@tree.command(guild=discord.Object(id=id_do_servidor), name='atualizar_trabalhos', description='Posta uma mensagem com a lista de trabalhos disponíveis.')
@app_commands.check(lambda interaction: interaction.client.has_required_role(interaction))
async def update_jobs(self, interaction: discord.Interaction):
    job_message = generate_job_message()
    await interaction.response.send_message(job_message, ephemeral=False)
            # Error handling
@update_jobs.error
async def update_jobs_error(self, interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)

@tree.command(guild=discord.Object(id=id_do_servidor), name='conceder_trabalho', description='Concede um trabalho disponível para uma conta.')
@app_commands.describe(job_name="Nome do trabalho para conceder", account_name="Nome da conta para associar ao trabalho")
async def claim_job(interaction: discord.Interaction, job_name: str, account_name: str):
    user_id = str(interaction.user.id)

    # Verify that the job exists
    if job_name not in job_slots:
        await interaction.response.send_message("Trabalho não encontrado! Verifique o nome e tente novamente.", ephemeral=False)
        return

    # Verify the account exists
    if user_id not in aclient.accounts or account_name not in aclient.accounts[user_id]:
        await interaction.response.send_message("Conta bancária não encontrada! Verifique o nome e tente novamente.", ephemeral=False)
        return

    # Check if the job is already at maximum capacity
    if aclient.jobs[job_name] >= job_slots[job_name]:
        await interaction.response.send_message(f"O trabalho '{job_name}' já está no limite de vagas!", ephemeral=False)
        return

    # Check if this account already has this job
    if "jobs" not in aclient.accounts[user_id][account_name]:
        aclient.accounts[user_id][account_name]["jobs"] = []

    if job_name in aclient.accounts[user_id][account_name]["jobs"]:
        await interaction.response.send_message(f"A conta '{account_name}' já está associada ao trabalho '{job_name}'.", ephemeral=False)
        return

    # Link the job to the specified bank account and save data
    aclient.accounts[user_id][account_name]["jobs"].append(job_name)
    aclient.jobs[job_name] += 1
    aclient.save_accounts()
    aclient.save_data(JOBS_FILE, aclient.jobs)

    # Generate an updated job message
    job_message = generate_job_message()
    await interaction.response.send_message(
        f"Você concedeu uma vaga em '{job_name}' para a conta '{account_name}'!\n\n{job_message}",
        ephemeral=False
    )

@tree.command(guild=discord.Object(id=id_do_servidor), name='criar_conta', description='Crie uma conta do banco!')
@app_commands.describe(account_name="Nome da nova conta")
async def create_account(interaction: discord.Interaction, account_name: str):
    try:
        user_id = str(interaction.user.id)
        if user_id not in aclient.accounts:
            aclient.accounts[user_id] = {}

        if account_name in aclient.accounts[user_id]:
            await interaction.response.send_message(f"Já existe uma conta chamada '{account_name}'.", ephemeral=False)
        else:
            aclient.accounts[user_id][account_name] = {
                "balance": 20, "max_salary": 0, "last_salary_time": None
            }
            aclient.save_accounts()
            await interaction.response.send_message(f"Conta '{account_name}' criada com sucesso!", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"Erro ao criar conta: {e}", ephemeral=True)

@tree.command(guild=discord.Object(id=id_do_servidor), name='deletar_conta', description='Deleta uma conta')
@app_commands.describe(account_name="Nome da conta a ser deletada")
async def delete_account(interaction: discord.Interaction, account_name: str):
            user_id = str(interaction.user.id)

            if user_id in aclient.accounts and account_name in aclient.accounts[user_id]:
                # Check for jobs associated with the account and update job slots
                account = aclient.accounts[user_id][account_name]
                if "jobs" in account:
                    for job in account["jobs"]:
                        if job in aclient.jobs and aclient.jobs[job] > 0:
                            aclient.jobs[job] -= 1  # Decrement the job slot count
                    # Save job data after updating slot counts
                    aclient.save_data(JOBS_FILE, aclient.jobs)

                # Delete the account from the accounts data
                del aclient.accounts[user_id][account_name]
                aclient.save_accounts()  # Save accounts data after deleting the account

                await interaction.response.send_message(f"A conta '{account_name}' foi deletada com sucesso.", ephemeral=False)
            else:
                await interaction.response.send_message("Conta não encontrada! Verifique o nome da conta e tente novamente.", ephemeral=False)

@tree.command(guild=discord.Object(id=id_do_servidor), name='definir_salario', description='Define o salário máximo para uma conta.')
@app_commands.describe(account_name="Nome da conta", max_salary="Valor máximo do salário")
async def set_salary(interaction: discord.Interaction, account_name: str, max_salary: int):
    user_id = str(interaction.user.id)
    if user_id in aclient.accounts and account_name in aclient.accounts[user_id]:
        if max_salary > 0:
            aclient.accounts[user_id][account_name]["max_salary"] = max_salary
            aclient.save_accounts()  # Save to file after setting the max salary
            await interaction.response.send_message(f"Salário máximo de '{account_name}' definido para {max_salary} G.", ephemeral=False)
        else:
            await interaction.response.send_message("O salário máximo deve ser maior que 0.", ephemeral=False)
    else:
        await interaction.response.send_message("Conta não encontrada! Use o comando `/criar_conta` para criar uma nova conta.", ephemeral=False)

        @tree.command(guild=discord.Object(id=id_do_servidor), name='receber_salario', description='Recebe o salário da sua conta')
        @app_commands.describe(account_name="Nome da conta")
        async def receive_salary(interaction: discord.Interaction, account_name: str):
            user_id = str(interaction.user.id)
            if user_id in aclient.accounts and account_name in aclient.accounts[user_id]:
                account = aclient.accounts[user_id][account_name]
                max_salary = account.get("max_salary", 0)

                if max_salary <= 0:
                    await interaction.response.send_message("O salário não foi definido para esta conta. Use o comando /definir_salario para definir um valor.", ephemeral=False)
                    return

                # Check if the user can claim salary based on last claimed time
                now = datetime.now(TIMEZONE)
                last_salary_time = account.get("last_salary_time")

                if last_salary_time:
                    last_salary_time = datetime.fromisoformat(last_salary_time)
                    next_salary_time = last_salary_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

                    if now < next_salary_time:
                        await interaction.response.send_message("Você só pode receber seu salário novamente após a meia-noite (Horário de São Paulo).", ephemeral=False)
                        return

                # Calculate the salary
                salary = random.randint(1, max_salary)
                if salary < 50:
                    bonus = random.randint(1, max_salary // 2)
                    salary += bonus

                # Update account balance and last salary time
                account["balance"] += salary
                account["last_salary_time"] = now.isoformat()
                aclient.save_accounts()  # Save to file after receiving salary

                # Send balance update to linked channel if any
                await send_balance_update(user_id, account_name, salary, "adição de salário")

                await interaction.response.send_message(
                    f"Você recebeu {salary} G como salário! Saldo atual na conta '{account_name}': {account['balance']} G.",
                    ephemeral=False
                )
            else:
                await interaction.response.send_message("Conta não encontrada! Use o comando /criar_conta para criar uma nova conta.", ephemeral=False)

        @tree.command(guild=discord.Object(id=id_do_servidor), name='ver_gold', description='Verifica quantos golds você tem em uma das suas contas.')
        @app_commands.describe(account_name="Nome da conta para verificar")
        async def check_balance(interaction: discord.Interaction, account_name: str):
            user_id = str(interaction.user.id)
            if user_id in aclient.accounts and account_name in aclient.accounts[user_id]:
                balance = aclient.accounts[user_id][account_name]["balance"]
                await interaction.response.send_message(f"Você tem {balance} G na conta '{account_name}'.", ephemeral=False)
            else:
                await interaction.response.send_message("Conta não encontrada! Use o comando /criar_conta para criar uma nova conta.", ephemeral=False)

@tree.command(guild=discord.Object(id=id_do_servidor), name='link_channel', description='Vincula uma conta do banco a um canal para atualizações.')
@app_commands.describe(account_name="Nome da conta para associar", channel_id="ID do canal para receber atualizações")
async def link_channel(interaction: discord.Interaction, account_name: str, channel_id: int):
                user_id = str(interaction.user.id)

                # Verify that the account exists
                if user_id not in aclient.accounts or account_name not in aclient.accounts[user_id]:
                    await interaction.response.send_message("Conta bancária não encontrada! Verifique o nome e tente novamente.", ephemeral=False)
                    return

                # Link the account to the specified channel
                aclient.accounts[user_id][account_name]["channel_id"] = channel_id
                aclient.save_accounts()

                await interaction.response.send_message(
                    f"A conta '{account_name}' foi vinculada ao canal com ID '{channel_id}'. Agora você receberá atualizações nesse canal.",
                    ephemeral=False
                )

async def send_balance_update(user_id: str, account_name: str, amount: int, transaction_type: str):
            """Send a message to the linked channel when a balance update occurs."""
            account = aclient.accounts[user_id][account_name]
            channel_id = account.get("channel_id")

            # Only send message if account is linked to a channel
            if channel_id:
                # Retrieve the channel by its ID
                channel = aclient.get_channel(channel_id)
                if isinstance(channel, discord.TextChannel):  # Ensure it's a TextChannel
                    balance = account["balance"]
                    # Construct the message based on the transaction type
                    transaction_msg = f"{transaction_type.capitalize()} de {amount} G."
                    update_message = (
                        f"Conta '{account_name}' atualizada!\n"
                        f"{transaction_msg}\n"
                        f"Novo saldo: {balance} G."
                    )
                    await channel.send(update_message)

@tree.command(guild=discord.Object(id=id_do_servidor), name='alterar_dinheiro', description='Altera o valor do seu dinheiro')
@app_commands.describe(account_name="Nome da conta para alterar", amount="Valor para aumentar ou diminuir (use valor negativo para diminuir)")
async def alter_balance(interaction: discord.Interaction, account_name: str, amount: int):
            user_id = str(interaction.user.id)
            if user_id in aclient.accounts and account_name in aclient.accounts[user_id]:
                # Access the specific balance field in the account dictionary
                aclient.accounts[user_id][account_name]["balance"] += amount
                new_balance = aclient.accounts[user_id][account_name]["balance"]
                aclient.save_accounts()  # Save to file after modifying balance

                # Send balance update to linked channel if any
                transaction_type = "adição" if amount > 0 else "dedução"
                await send_balance_update(user_id, account_name, abs(amount), transaction_type)

                await interaction.response.send_message(f"O saldo da conta '{account_name}' foi alterado! Você agora tem {new_balance} G.", ephemeral=False)
            else:
                await interaction.response.send_message("Conta não encontrada! Use o comando /criar_conta para criar uma nova conta.", ephemeral=False)

@tree.command(guild=discord.Object(id=id_do_servidor), name='listar_contas', description='Lista todas as contas e golds')
async def list_accounts(interaction: discord.Interaction):
            user_id = str(interaction.user.id)
            if user_id in aclient.accounts and aclient.accounts[user_id]:
                # Extract only the account name and balance
                accounts_list = "\n".join([f"{name}: {info['balance']} G" for name, info in aclient.accounts[user_id].items()])
                await interaction.response.send_message(f"Suas contas:\n{accounts_list}", ephemeral=False)
            else:
                await interaction.response.send_message("Você não tem nenhuma conta. Use o comando `/criar_conta` para criar uma nova conta.", ephemeral=False)

@tree.command(guild=discord.Object(id=id_do_servidor), name='transferir_gold', description='Transfere golds entre contas')
@app_commands.describe(from_account="Nome da conta de origem", to_account="Nome da conta de destino", amount="Quantidade a transferir")
async def transfer_money(interaction: discord.Interaction, from_account: str, to_account: str, amount: int):
            user_id = str(interaction.user.id)
            if amount <= 0:
                await interaction.response.send_message("A quantidade para transferência deve ser maior que 0.", ephemeral=False)
                return

            if user_id in aclient.accounts:
                # Ensure from_account and to_account exist and get their balances
                if from_account in aclient.accounts[user_id] and to_account in aclient.accounts[user_id]:
                    if aclient.accounts[user_id][from_account]["balance"] >= amount:
                        # Perform the transfer
                        aclient.accounts[user_id][from_account]["balance"] -= amount
                        aclient.accounts[user_id][to_account]["balance"] += amount
                        aclient.save_accounts()  # Save to file after transfer
                        await interaction.response.send_message(
                            f"Transferência concluída! {amount} G foi transferido de '{from_account}' para '{to_account}'.",
                            ephemeral=False
                        )
                    else:
                        await interaction.response.send_message(f"Saldo insuficiente na conta '{from_account}'.", ephemeral=False)
                else:
                    await interaction.response.send_message("Uma das contas especificadas não existe. Verifique os nomes e tente novamente.", ephemeral=False)
            else:
                await interaction.response.send_message("Você não possui contas. Use o comando `/criar_conta` para criar uma nova conta.", ephemeral=False)

aclient.run('')