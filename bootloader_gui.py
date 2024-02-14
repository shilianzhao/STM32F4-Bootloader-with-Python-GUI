
import serial
import serial.tools.list_ports
import PySimpleGUI as sg

import binascii
import time

com_ports_DropDown_display = []
ser_gui = None

CIRCLE = '⚫'           # Error status LED

for port in serial.tools.list_ports.comports():
    com_ports_DropDown_display.append(port.name+', '+ port.manufacturer)

#sg.theme('DarkTeal 7')
#sg.theme('LightBlue2')    
sg.theme('BlueMono')
window_layout = [
    #[sg.Text('Designed by Steven Shilian ZHAO', font=('Any',11), pad=(90,60))],

    [
     sg.Text('Choose Available Ports', font=('Calibri',12,'bold'), pad=(90,40)),  
     sg.Combo(values=com_ports_DropDown_display, font=('Calibri',12,), size=(30, 3), key='-BOOTLOADER CHOSEN PORTS-', enable_events=True,), # sg.DropDown is another name
     sg.Button(' Connect Port ', key='-CONNECT PORT BUTTON-', font=('Calibri',12, 'bold'), pad=(90,40), disabled=True) 
    ],
    
    [sg.FileBrowse(' Choose Bin File ', key='-BIN FILE BROWSE-', target='-BIN FILE PATH-', font=('Calibri',12,'bold'), pad=(90,10), file_types=(("BIN Files", "*.bin"),), enable_events=True, disabled=True),
     sg.InputText('  ', key='-BIN FILE PATH-', size=(130, 1), font=('Calibri', 12), pad=(42, 10), text_color='white', readonly=True, disabled_readonly_background_color=sg.theme_background_color(), enable_events=True)  ],

    [sg.Button(' Download Firmware ', key='-DOWNLOAD FIRMWARE BUTTON-', font=('Calibri',12, 'bold'), pad=(90,40), enable_events=True, visible=True, disabled=True), 
     sg.ProgressBar(1000, key='-PROGRESS BAR-', orientation='h', bar_color=('#32414B', 'white'), size=(50,15), pad=(5,40))  ],

    [sg.Text(' Operation Information ', key='-OPERATING INFORMATION TEXT-', font=('Calibri',12,'bold'), pad=(335,10), visible=True) ],

    [
        sg.Text('by Steven Shilian ZHAO', font=('Any',10), pad=(60,20), text_color='Blue'),
        sg.Multiline('', key='-MULTILINE-', size=(370,16), font=('Calibri', 11), pad=(60,20), enable_events=True)
    ]
]

def reset_S(sp1):           # S stand for Steven new function
    sp1.setDTR(0)
    time.sleep(0.1)
    sp1.setDTR(1)
    time.sleep(0.5)

def _wait_for_ask(sp1, info = ""):
    # wait for ask
    try:
        ask = ord(sp1.read())
        print(ask)
    except:
        raise Exception("Can't read port or timeout")
    else:
        if ask == 0x79:
            # ACK
            return 1
        else:
            if ask == 0x1F:
                # NACK
                raise Exception("NACK "+info)
            else:
                # Unknown responce
                raise Exception("Unknown response. "+info+": "+hex(ask))


def initChip_S(sp):         # S stand for Steven new function
    # Set boot
    sp.setRTS(0)
    reset_S(sp)
    send_data = b'\x7F'
    sp.write(send_data)      # failed in test/debug by steven 
    return _wait_for_ask(sp, "Syncro")        

def stm32F411_bootloader_handshake(): # hand shake with stm bootloader
    global ser_gui

    try:
        initChip_S(ser_gui)     
        print("successful handshake, initChip")    
    except Exception as exception :
        print(exception.__class__.__name__)

def int_to_hex_bootloaderHandler(i):
        if(0<=i<16):
            temp1 = i%16
            if temp1<10:
                pass
            if temp1 ==10:
                temp1 = 'a'
            if temp1 ==11:
                temp1 = 'b'
            if temp1 ==12:
                temp1 = 'c'
            if temp1 ==13:
                temp1 = 'd'
            if temp1 ==14:
                temp1 = 'e'
            if temp1 ==15:
                temp1 = 'f'

            i_str1 = str(temp1)
            i_int_pad1 = i_str1.zfill(2)
            i_binary1 = bytes(i_int_pad1, 'ascii')
            i_hex = binascii.unhexlify(i_binary1)
            return i_hex
            #list.append(i_hex)

        elif (16<= i <256):
            #i_original = i
            temp = i//16
            if temp <=9:
                pass
            if temp ==10:
                temp = 'a'
            if temp ==11:
                temp = 'b'
            if temp ==12:
                temp = 'c'
            if temp ==13:
                temp = 'd'
            if temp ==14:
                temp = 'e'
            if temp ==15:
                temp = 'f'
            i_int_1 = temp

            temp = i%16
            if temp <=9:
                pass
            if temp ==10:
                temp = 'a'
            if temp ==11:
                temp = 'b'
            if temp ==12:
                temp = 'c'
            if temp ==13:
                temp = 'd'
            if temp ==14:
                temp = 'e'
            if temp ==15:
                temp = 'f'
            i_int_0 = temp
            
            i_str_1 = str(i_int_1)
            i_str_0 = str(i_int_0)
            i_str = i_str_1 + i_str_0
             
            i_binary = bytearray(i_str, 'ascii')
            i_hex = binascii.unhexlify(i_binary)
            return i_hex

def _wait_for_ask_bootloaderHandler(sp1, info = ""):
    # wait for ask
    try:
        ask = ord(sp1.read())
        #print(ask)
    except:
        raise Exception("Can't read port or timeout")
    else:
        if ask == 0x79:
            # ACK
            return 1
        else:
            if ask == 0x1F:
                # NACK
                raise Exception("NACK "+info)
            else:
                # Unknown responce
                raise Exception("Unknown response. "+info+": "+hex(ask))


def cmdGeneric_bootloaderHandler(sp1, cmd):     
    sp1.write(int_to_hex_bootloaderHandler(cmd))
    sp1.write(int_to_hex_bootloaderHandler(cmd ^ 0xFF))        # Control byte
    return _wait_for_ask_bootloaderHandler(sp1, hex(cmd))


def cmdExtendedEraseMemory_bootloaderHandler(sp):
    if cmdGeneric_bootloaderHandler(sp, 0x44):          # masked by steven
        #mdebug("*** Extended Erase memory command")
        # Global mass erase
        """
        sp.write(int_to_hex_bootloaderHandler(0xFF))
        sp.write(int_to_hex_bootloaderHandler(0xFF))
        # Checksum
        sp.write(int_to_hex_bootloaderHandler(0x00))
        """

        # erase Section 0 to 5 
        
        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of pages/sections N =5, actually erase pages is N + 1 = 6.
        sp.write(int_to_hex_bootloaderHandler(0x05))

        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of Section 0
        sp.write(int_to_hex_bootloaderHandler(0x00)) 
        
        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of Section 1
        sp.write(int_to_hex_bootloaderHandler(0x01)) 

        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of Section 2
        sp.write(int_to_hex_bootloaderHandler(0x02))

        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of Section 3
        sp.write(int_to_hex_bootloaderHandler(0x03)) 

        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of Section 4
        sp.write(int_to_hex_bootloaderHandler(0x04))

        sp.write(int_to_hex_bootloaderHandler(0x00))            # number of Section 5
        sp.write(int_to_hex_bootloaderHandler(0x05)) 

        # Checksum
        sp.write(int_to_hex_bootloaderHandler(0x04))            # manually calculated and got the result as 0x04 
        
        tmp = sp.timeout
        sp.timeout = 30
        print("Extended erase (0x44), this can take ten seconds or more")
        _wait_for_ask_bootloaderHandler(sp, "0x44 erasing failed")
        sp.timeout = tmp
        #mdebug("    Extended Erase memory done")
    else:
        raise Exception("Extended Erase memory (0x44) failed")

def _encode_addr_bootloaderHandler( addr):
    byte3 = (addr >> 0) & 0xFF
    byte2 = (addr >> 8) & 0xFF
    byte1 = (addr >> 16) & 0xFF
    byte0 = (addr >> 24) & 0xFF
    crc = byte0 ^ byte1 ^ byte2 ^ byte3
    #return (chr(byte0) + chr(byte1) + chr(byte2) + chr(byte3) + chr(crc))  # this is original python 2 codes
    address_and_checksum = [byte0, byte1, byte2,byte3,crc]
    return address_and_checksum


def cmdReadMemory_bootloaderHandler(sp, addr, lng):
    assert(lng <= 256)
    if cmdGeneric_bootloaderHandler(sp, 0x11):
        #mdebug("*** ReadMemory command")
        sp.write(_encode_addr_bootloaderHandler(addr))
        _wait_for_ask_bootloaderHandler(sp, "0x11 address failed")
        N = (lng - 1) & 0xFF
        crc = N ^ 0xFF
        sp.write(int_to_hex_bootloaderHandler(N) + int_to_hex_bootloaderHandler(crc))
        _wait_for_ask_bootloaderHandler(sp, "0x11 length failed")
        data_read = sp.read(lng)
        return data_read
    else:
        raise Exception("ReadMemory (0x11) failed")


def readMemory_bootloaderHandler(sp2, addr, lng):
    lng_init = lng

    data_bytearray_sum = bytearray()
    print(type(data_bytearray_sum))
    while lng > 256:
        #mdebug("Read %(len)d bytes at 0x%(addr)X" % {'addr': addr, 'len': 256})
        data_bytes = cmdReadMemory_bootloaderHandler(sp2, addr, 256)
        data_bytearray = bytearray(data_bytes) 
        data_bytearray_sum.extend(data_bytearray)
        addr = addr + 256
        progress_bar_current_value = ((lng_init/256 - lng/256)/(lng_init/256))*1000    # dig down into
        firmware_update_progress_bar.update(progress_bar_current_value)
        lng = lng - 256
            
    #mdebug("Read %(len)d bytes at 0x%(addr)X" % {'addr': addr, 'len': lng})
    data_bytes = cmdReadMemory_bootloaderHandler(sp2, addr, lng)
    data_bytearray = bytearray(data_bytes) 
    data_bytearray_sum.extend(data_bytearray)
    data_bytes_return = bytes(data_bytearray_sum)
    firmware_update_progress_bar.update(1000)
    return data_bytes_return

def cmdWriteMemory_bootloaderHandler(sp, addr, data):      #write all the data, can be < 256
    assert(len(data) <= 256)
    if cmdGeneric_bootloaderHandler(sp, 0x31):  #masked by steven
        #mdebug("*** Write memory command")
        sp.write(_encode_addr_bootloaderHandler(addr))
        _wait_for_ask_bootloaderHandler(sp, "0x31 address failed")
        
        """ send the number of bytes to be written.
            note: this number is the real sent (number -1) 
            for instance: when you are goint to send 100 bytes, here the number to be written is 100-1 = 99
        """
        lng_int = (len(data)-1) & 0xFF
        lng_hex = int_to_hex_bootloaderHandler(lng_int)
        sp.write(lng_hex)  
        
        crc_int = lng_int           # crc_int is the first number/data for crc calculation, crc_int is being prepared for later crc calculating 

        for c_int in data:
            crc_int = crc_int ^ c_int
            c_hex = int_to_hex_bootloaderHandler(c_int)
            sp.write(c_hex)                  # STEVEN chr(c) ---> c

        crc_hex = int_to_hex_bootloaderHandler(crc_int)
        sp.write(crc_hex)                    # STEVEN chr(crc) ---> crc
        #print("crc_hex: %s" % crc_hex) 

        _wait_for_ask_bootloaderHandler(sp, "0x31 programming failed")
        #mdebug("    Write memory done")
    else:
        raise Exception("Write memory (0x31) failed")


def writeMemory_bootloaderHandler(sp2, addr, data):      # decompose the data into pages 
    lng = len(data)
    lng_init = lng
    offs = 0
    while lng > 256:
        #mdebug("Write %(len)d bytes at 0x%(addr)X" % {'addr': addr, 'len': 256})    # steven moved
        cmdWriteMemory_bootloaderHandler(sp2,addr, data[offs:offs+256])
        offs = offs + 256
        addr = addr + 256
        progress_bar_current_value = ((lng_init/256 - lng/256)/(lng_init/256))*1000    # 
        firmware_update_progress_bar.update(progress_bar_current_value)

        lng = lng - 256

    if lng > 0:     #steven added
        #mdebug("Write %(len)d bytes at 0x%(addr)X" % {'addr': addr, 'len': lng})     # 256 -> len
        cmdWriteMemory_bootloaderHandler(sp2, addr, data[offs:offs+lng])
        firmware_update_progress_bar.update(1000)


window = sg.Window("Bootloader GUI by Steven Shilian ZHAO" , window_layout, resizable=True, size = (1024,600), margins=(1,1), finalize=True, return_keyboard_events=True)

firmware_update_progress_bar = window['-PROGRESS BAR-']


while True:
    
    event, values = window.read()

    # Check the window is closed
    if event is None or event == sg.WIN_CLOSED:
        if ser_gui!= None:
            ser_gui.close()
        print("Application Closed")
        break


    if event == '-BOOTLOADER CHOSEN PORTS-':
        connect_button: sg.Button = window['-CONNECT PORT BUTTON-']
        connect_button.update(disabled=False)
        #window['-CONNECT PORT BUTTON-'].update(disabled=False)



    # Connect the COM
    if event == '-CONNECT PORT BUTTON-':
        com_ports_DropDown_display_current = values['-BOOTLOADER CHOSEN PORTS-']
        
        com_ports_DropDown_display_split = com_ports_DropDown_display_current.split(",")
        ser_gui = serial.Serial(port = com_ports_DropDown_display_split[0], baudrate = 115200, bytesize=8, parity = 'N', stopbits=1, timeout=0.25)
        #values['-MULTILINE-'] = "Connect done!"
        #window['-MULTILINE-'].update(values['-MULTILINE-'] +'\nConnected done!')
        window['-MULTILINE-'].update('Connected done!', append=True)
        window['-BIN FILE BROWSE-'].update(disabled=False)
        

    if event == '-BIN FILE PATH-':
        window['-DOWNLOAD FIRMWARE BUTTON-'].update(disabled=False)


    if event == '-DOWNLOAD FIRMWARE BUTTON-':
        string_file = values['-BIN FILE PATH-']

        values['-MULTILINE-'] = "Erase flash" 
        window['-MULTILINE-'].update(values["-MULTILINE-"] +'\nErase started ... ...')
        bin_file = open(string_file,'rb')
        data = bin_file.read()

        #serialHandler.ser.parity = serialHandler.serial.PARITY_EVEN
        ser_gui.parity = serial.PARITY_EVEN

        # handshake to STM32F411 bootloader
        stm32F411_bootloader_handshake()
        window['-MULTILINE-'].update('\nBootloader handshake completed.', append=True)

        # erase entire flash
        window['-MULTILINE-'].update('\nFlash erase started ... ...', append=True)
        cmdExtendedEraseMemory_bootloaderHandler(ser_gui)             # erase entire flash  
        window['-MULTILINE-'].update('\nFlash erase completed !', append=True)

        # write firmware to flash
        window['-MULTILINE-'].update('\nFlash writing started ... ...', append=True)

        #bootloaderHandler.writeMemory(serialHandler.ser, 0x8000000, data)
        writeMemory_bootloaderHandler(ser_gui, 0x8000000, data)
        window['-MULTILINE-'].update('\nFlash writing completed!', append=True)

        # read flash and verify
        window['-MULTILINE-'].update('\nFirmware writing verification started ... ...', append=True)
        
        verify = readMemory_bootloaderHandler(ser_gui, 0x8000000, len(data))
        if(data == verify):
            print( "Writing Verification OK")
            window['-MULTILINE-'].update('\nFirmware write verification completed!', append=True)
        else:
            print( "Flash Writing Verification FAILED")
            window['-MULTILINE-'].update('\nFirmware writing verification FAILED', append=True)
            print( str(len(data)) + ' vs ' + str(len(verify)))
            for i in range(0, len(data)):
                if data[i] != verify[i]:
                    print( hex(i) + ': ' + hex(data[i]) + ' vs ' + hex(verify[i]))
        
        print('verifying is ok')        

        ser_gui.parity = serial.PARITY_NONE

window.close()
