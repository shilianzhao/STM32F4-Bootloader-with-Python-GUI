# STM32F4 Bootloader with Python GUI
 STM32 Bootloader GUI based Python
 Python script which creates GUI to talk to the STM32 bootloader to download firmware from PC to STM32 microcontrollers over UART. This is tested with STM32F401, but it applied to almost all STM32 series: STM32F0/F1/F2/F3/F4/G0/G4/H7/L0/L1/L4. 
## 1. Project folder
 Local computer: C:\Users\Owner\OneDrive\Documents\STM32F4_Bootloader
 
 Github: https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI
## 2. Hardware settings
 Microcontroller: 	STM Nucleo-F401RE
 USB to UART adapter: 	Adafruit USB to TTL Serial Cable

![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/1aba1baf-40ac-4784-a077-ea5c8fc340fc)
![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/9995b591-6fec-4b1d-875a-48b95157026c)

## 3. STM32F4 Bootloader basics
### 3.1. Boot mode
 At startup, boot pins are used to select one out of three boot options:
  * Boot from user Flash
		* Boot from system memory, this is the Bootloader mode. 
		* Boot form embedded SRAM	
How to configure the microcontroller to the different boot mode? Here it is:

![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/31ee672d-6f69-412f-ac65-4d2498eb2cc3)
  - from RM0368: STM32F401 Reference manual.
    
 So now, we configure BOOT0 Pin60 (F401) to 3.3V, and set BOOT1 Pin28/PB2 (F401) to Gnd. 
 ST company burned the bootloader code to the System Memory before shipping to customer. 
	In Bootloader mode, when microcontroller power on, the bootloader firmware which is already burned in the system memory starts run. This firmware is waiting for the first handshake command from outside device.

 ### 3.2. Boot mode firmware memory location
  Where is the bootloader firmware located?   It starts from address 0x1FFF 0000, total 29 Kbyte. This location section name is called System Memory.
  
 ![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/cceebe08-e9e6-471a-b2b3-00103d8b71ed)
   - from STM32F401 Datasheet
  Usually, the user application code starts from Flash 0x0800 0000.

## 4. Software

The python script calls ST bootloader commands to download the bin file to STM32F4 microcontrollers. 
Development tolls and python modules: 
Python 3.12.1
VS Code version: 1.86.1
pyserial: python library for serial port handling
	         installation command:  python -m pip install pyserial
PySimpleGUI: Python package that enables Python programmers to create GUIs
             Installation command: python -m pip install pysimplegui

The Bootloader GUI is shown below:

![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/e3ac59d9-e264-46fd-8c64-f741bd8741b5)

## Video
https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/2e38246f-5bcb-4cc2-aa19-05f42dfaeb3f

## 5. How to test codes

1.	Set Boot0 = 0, Boot1 = 0, connect USB cable from PC to Nucleo-F401 board. 
2.	Use STM32CubeProgrammer to check/read the current codes in the Flash 0x0800 0000.
3.	Set Boot0 = 1, Boot1 = 0, add new connect of Adafruit adapter from PC to Nucleo-F401 UART1 port.
4.	Run the python code to download the “NucleoF401_Blinking_Steven_0x0ED8_bytes.bin” to Nucleo-F401.
5.	Set Boot0 = 0, Boot1 = 0, turn the Nucleo_F401 board. At this time, the Nucleo-F401 board user led should blink.
6.	You can also use the STM32CubeProgrammer to read the code in Flash from the 0x0800 0000 to compare the codes to the previous one.
![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/0c9aba68-56f1-4aab-a28b-1e6a44985f07)
7. You can also use Hex Editor Neo to read and edit the bin file as shown below:

   ![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/9266686c-871a-4823-bc2f-de97122df7c1)

## 6. Extra tool
 AccessPort is useful for sending STM Bootloader command one-by-one to F411 Nucleo board.
![image](https://github.com/shilianzhao/STM32F4-Bootloader-with-Python-GUI/assets/31520270/61d57b08-9166-47da-bdd0-f218560e64da)

## 7. Reference
* ST AN2606: STM32 microcontroller system memory boot mode
* ST AN3155: USART protocol used in STM32 bootloader
* https://github.com/florisla/stm32loader florisla     very important
* https://github.com/jsnyder/stm32loader/blob/master/stm32loader.py, jsnyder
* https://github.com/pavelrevak/stm32bl/blob/ae908e34cdb727808817d2d04a6dbc752a5b22f8/README.md
* https://www.youtube.com/watch?v=GR8Vy5QvDHU STM32 Tips: Talking to the on-board Bootloader

  


 



  


 
