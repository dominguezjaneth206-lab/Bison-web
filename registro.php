
<?php header("Content-Type: text/html; charset=UTF-8"); ?>
<?php

header("Content-Type: text/html; charset=UTF-8");

// Conexión a la BD
$conexion = new mysqli("localhost", "root", "", "usuarios_db");

if ($conexion->connect_error) {
    die("Error de conexión: " . $conexion->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Código para procesar datos
} else {
    // Responder con error o redirigir
    header("HTTP/1.1 405 Method Not Allowed");
    exit();
}

// Recibir datos del formulario
$usuario = $_POST['usuario'];
$correo = $_POST['correo'];
$contrasena = password_hash($_POST['contrasena'], PASSWORD_DEFAULT);  // Seguridad

// Insertar datos
$sql = "INSERT INTO usuarios (usuario, correo, contrasena) VALUES (?, ?, ?)";
$stmt = $conexion->prepare($sql);
$stmt->bind_param("sss", $usuario, $correo, $contrasena);

if ($stmt->execute()) {
    echo "<h2>Registro exitoso</h2>";
    echo "<a href='Prinncipal.html'>Iniciar sesión</a>";
} else {
    echo "Error al registrar: " . $conexion->error;
}

$stmt->close();
$conexion->close();
?>


