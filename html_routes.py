from flask import send_from_directory, Response
import os

def register_html_routes(app):
    """Registra las rutas HTML en la aplicación Flask"""
    
    @app.route('/test')
    def test_route():
        return '<h1>TEST OK - Flask está funcionando!</h1>'
    
    @app.route('/login')
    def login_page():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Fleet</title>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                }
                .login-box {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    width: 350px;
                }
                h1 { text-align: center; color: #333; }
                input {
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    box-sizing: border-box;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                button:hover { background: #5a67d8; }
                .demo { 
                    margin-top: 20px; 
                    padding: 10px; 
                    background: #f5f5f5; 
                    border-radius: 5px;
                    text-align: center;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h1>🚚 Fleet Login</h1>
                <form id="loginForm">
                    <input type="email" id="email" placeholder="Email" value="demo@loginexia.com" required>
                    <input type="password" id="password" placeholder="Password" value="demo123" required>
                    <button type="submit">Iniciar Sesión</button>
                </form>
                <div class="demo">
                    <strong>Demo:</strong><br>
                    demo@loginexia.com / demo123
                </div>
            </div>
            <script>
                document.getElementById('loginForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    try {
                        const response = await fetch('/api/auth/login', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                email: document.getElementById('email').value,
                                password: document.getElementById('password').value
                            })
                        });
                        const data = await response.json();
                        if (data.access_token) {
                            localStorage.setItem('fleet_token', data.access_token);
                            alert('Login exitoso!');
                            window.location.href = '/dashboard';
                        } else {
                            alert('Error: ' + (data.error || 'Login failed'));
                        }
                    } catch (error) {
                        alert('Error de conexión');
                    }
                });
            </script>
        </body>
        </html>
        """
        return Response(html, mimetype='text/html')
    
    @app.route('/dashboard')
    def dashboard_page():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - Fleet</title>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    background: #f5f5f5;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .container {
                    padding: 20px;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }
                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }
                button {
                    background: white;
                    color: #667eea;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚚 Fleet Dashboard</h1>
                <button onclick="logout()">Logout</button>
            </div>
            <div class="container">
                <h2>Bienvenido!</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">156</div>
                        <div>Repartidores</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">1,247</div>
                        <div>Entregas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">28 min</div>
                        <div>Tiempo Promedio</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">7</div>
                        <div>Alertas</div>
                    </div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px;">
                    <h3>Estado API:</h3>
                    <pre id="api">Cargando...</pre>
                </div>
            </div>
            <script>
                if (!localStorage.getItem('fleet_token')) {
                    alert('No hay sesión');
                    window.location.href = '/login';
                }
                function logout() {
                    localStorage.clear();
                    window.location.href = '/login';
                }
                fetch('/health').then(r => r.json()).then(data => {
                    document.getElementById('api').textContent = JSON.stringify(data, null, 2);
                });
            </script>
        </body>
        </html>
        """
        return Response(html, mimetype='text/html')
    
    print("✅ Rutas HTML registradas: /test, /login, /dashboard")
