Se documentan a continuación los datos necesarios para el manejo de los códigos desarrollados para el funcionamiento del modulo didactico.

Se presenta el archivo ***sensores.py***, aquí se hace uso del paradigma de programación orientada a objetos POO, se han desarrollado clases para cada sensor o actuador del modulo, no se debe realizar ningún cambio a este archivo. 
En el archivo ***main.py*** se desarrolla toda la lógica del funcionamiento del modulo, la programación se realiza con el paradigma de programación estructurada,  este paradigma es sencillo de entender para ingenieros electrónicos puesto que gran parte de la electrónica digital sigue este principio. 

Si se desea cambiar el funcionamiento del modulo solo es necesario cambiar la estructura de este archivo fuente. En este archivo se importa el archivo sensores.py y posteriormente se invoca la clase y el metodo que sean requeridos, se debe ser cuidadoso de pasar los atributos adecuadamente.

# Librerias necesarias

Dentro de los archivos se puede observar que se han importado algunas librerias.

La libreria para el manejo de la pantalla OLED TFT debe ser descargada del siguiente link (creditos russhughes) https://github.com/russhughes/st7789_mpy/tree/master, se presentan los archivos en crudo .C o a manera de firmware .bin, se recomiendo usar la segunada opción. Para la utilización del firmware es necesario usar alguna herramienta para grabarlo en el microcontrolador. Dentro de la carpeta ***extras*** se puede encontrar el firmware que se utilizó en esta placa.