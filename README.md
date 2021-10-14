Este es el bot oficial del servidor de migala.

Para ejecutar el bot se requiere de un archivo de configuracion 
de nombre `settings.json`:
#### _Configuracion Formato Json_
```json
{
  "prefix": "prefijo para los comandos del bot",
  "token": "token del bot de discord",
  "mongoUser": "usuario de la base de datos (MongoDB)",
  "mongoPassword": "contraseña de la base de datos (MongoDB)",
  "dev_ids": "lista de ids con permisos de desarrollador: aviso de bugs, comando stop",
  "guild_ids": "lista de ids de los servidores en donde se pueden utilizar los SlashCommands"
}
```