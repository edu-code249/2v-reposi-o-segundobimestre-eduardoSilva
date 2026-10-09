from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required
import database


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not nome or not email or not senha:
            flash("Todos os campos são obrigatórios.", "danger")
            return redirect(url_for("auth.registro"))

        usuario_existente = database.buscar_usuario_por_email(email)
        
        if not usuario_existente:
            senha_criptografada = generate_password_hash(senha, method='scrypt')
            
            database.criar_usuario(nome=nome, email=email, password=senha_criptografada)
            
            flash("Cadastro realizado com sucesso! Faça login.")
            return redirect(url_for("auth.login"))
        
        else:
            flash("Este e-mail já está cadastrado.")
            return redirect(url_for("auth.registro"))

    return render_template("registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form["senha"]
        email = request.form["email"]
        usuario = database.buscar_usuario_por_email(email=email)

        usuario = database.buscar_usuario_por_email(email)
        
        if usuario and check_password_hash(usuario.password, senha):
            login_user(usuario)
            flash('Login realizado com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha incorretos.')
            return redirect(url_for('auth.login'))
        
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash('Você saiu da sua conta.')
    return redirect(url_for('auth.login'))
