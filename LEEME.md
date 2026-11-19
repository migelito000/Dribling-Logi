# Dribling Logi · salas 1v1

## Probar hoy desde dos casas

Con Python 3.12 y [cloudflared](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/) instalados en tu computadora:

1. Abrí una terminal en la carpeta descomprimida. Ejecutá `python -m pip install -r requirements.txt` y después `python server.py`. Dejá esa terminal abierta.
2. En otra terminal ejecutá `cloudflared tunnel --url http://127.0.0.1:8080`. Copiá la dirección HTTPS terminada en trycloudflare.com que aparece en la terminal y abrila vos en el navegador.
3. En **Jugar → Sala online** pulsá **Copiar enlace**. Mandale ese enlace a tu amigo. Tu amigo solo necesita el navegador. Elijan un auto cada uno y pulsen **Estoy listo**.
4. Dejá abiertas las dos terminales y la pestaña del juego mientras juegan. Cuando cierres el túnel caducará la dirección pública.

[Guía oficial de túneles temporales](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

## Publicar en Render

1. Descomprimí el ZIP. Subí index.html, server.py, requirements.txt y render.yaml a la raíz de un repositorio de GitHub. Podés usar un repositorio privado.
2. Entrá a https://dashboard.render.com y elegí **New → Blueprint**. Conectá el repositorio y confirmá la creación del servicio gratuito definido en render.yaml.
3. Cuando el servicio figure como **Live**, abrí su dirección HTTPS. En el juego entrá en **Jugar → Sala online → Copiar enlace** y enviáselo a tu amigo.
4. Tu amigo entra directamente como J2. Cada uno elige su auto con las flechas. J1 elige el deporte y la pelota. Cuando ambos pulsan **Estoy listo**, arranca la partida.

El plan gratuito puede tardar en despertar al abrir el juego después de un período sin actividad. Conservá una sola instancia del servidor para que los dos lleguen a la misma sala.

## Probar en una computadora

Con Python 3.12, abrí una terminal en la carpeta descomprimida y ejecutá:

    python -m pip install -r requirements.txt
    python server.py

Abrí http://localhost:8080 en una ventana y el enlace de invitación en otra. Para probar en dos equipos de la misma Wi-Fi, el anfitrión debe entrar con la IP local de su computadora en vez de localhost (por ejemplo http://192.168.1.10:8080). Para jugar desde distintas casas, usá el enlace HTTPS del servicio publicado.

## Controles y partidas

Cada dispositivo controla su propio auto con teclado, joystick o botones táctiles. Con teclado usá A/D o ←/→ para moverte, W o espacio para saltar, S o Shift para el turbo y E para girar. Con joystick, usá el stick izquierdo, el botón inferior para saltar, el botón izquierdo para girar y el gatillo derecho para el turbo.

J1 calcula la física y tiene que mantener el juego en primer plano. La sala se cierra cuando sale cualquiera de los dos. Al terminar, **Revancha** vuelve a la selección de autos con el mismo enlace. Las partidas online amistosas no otorgan monedas.
