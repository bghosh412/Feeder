# DS3231 RTC Handler
# Manages real-time clock for scheduled feedings
from machine import I2C, Pin
import struct

class DS3231:
    """Driver for DS3231 Real-Time Clock module"""
    
    ADDRESS = 0x68
    
    def __init__(self, sda_pin, scl_pin):
        """Initialize I2C connection to DS3231"""
        self.i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        
    def _bcd_to_dec(self, bcd):
        """Convert BCD to decimal"""
        return (bcd // 16) * 10 + (bcd % 16)
    
    def _dec_to_bcd(self, dec):
        """Convert decimal to BCD"""
        return (dec // 10) * 16 + (dec % 10)
    
    def get_time(self):
        """
        Get current time from RTC
        Returns: (year, month, day, hour, minute, second, weekday)
        """
        # Read 7 bytes starting from register 0x00
        data = self.i2c.readfrom_mem(self.ADDRESS, 0x00, 7)
        
        second = self._bcd_to_dec(data[0] & 0x7F)
        minute = self._bcd_to_dec(data[1])
        hour = self._bcd_to_dec(data[2] & 0x3F)
        weekday = self._bcd_to_dec(data[3])
        day = self._bcd_to_dec(data[4])
        month = self._bcd_to_dec(data[5] & 0x1F)
        year = self._bcd_to_dec(data[6]) + 2000
        
        return (year, month, day, hour, minute, second, weekday)
    
    def set_time(self, year, month, day, hour, minute, second, weekday=1):
        """Set RTC time"""
        data = bytearray(7)
        data[0] = self._dec_to_bcd(second)
        data[1] = self._dec_to_bcd(minute)
        data[2] = self._dec_to_bcd(hour)
        data[3] = self._dec_to_bcd(weekday)
        data[4] = self._dec_to_bcd(day)
        data[5] = self._dec_to_bcd(month)
        data[6] = self._dec_to_bcd(year - 2000)
        
        self.i2c.writeto_mem(self.ADDRESS, 0x00, data)
    
    def get_temperature(self):
        """Get temperature from DS3231's built-in sensor"""
        data = self.i2c.readfrom_mem(self.ADDRESS, 0x11, 2)
        return data[0] + (data[1] >> 6) * 0.25
    
    def set_alarm(self, hour, minute):
        """Set alarm for specific time (Alarm 1)"""
        data = bytearray(4)
        data[0] = self._dec_to_bcd(0)  # Seconds
        data[1] = self._dec_to_bcd(minute)
        data[2] = self._dec_to_bcd(hour)
        data[3] = 0x80  # Alarm when hours, minutes, and seconds match
        
        self.i2c.writeto_mem(self.ADDRESS, 0x07, data)
        
        # Enable alarm interrupt
        control = self.i2c.readfrom_mem(self.ADDRESS, 0x0E, 1)[0]
        control |= 0x05  # Enable alarm 1 interrupt
        self.i2c.writeto_mem(self.ADDRESS, 0x0E, bytes([control]))
    
    def clear_alarm(self):
        """Clear alarm flag"""
        status = self.i2c.readfrom_mem(self.ADDRESS, 0x0F, 1)[0]
        status &= 0xFE  # Clear alarm 1 flag
        self.i2c.writeto_mem(self.ADDRESS, 0x0F, bytes([status]))
