import random
import string
import base64
import re
import hashlib

class LuaObfuscator:
    def __init__(self, level=10):
        self.level = level
        self.var_counter = 0
        self.var_mapping = {}
        
    def generate_random_name(self, length=None):
        """Generate nama variabel acak yang tetap valid di Lua"""
        if length is None:
            length = random.randint(12, 20)
        
        # Karakter yang membingungkan AI
        confusing = ['l', 'I', 'i', 'O', 'o', '0', '1']
        chars = string.ascii_letters + '_'
        
        # Nama harus dimulai dengan huruf atau underscore
        name = random.choice(string.ascii_letters + '_')
        
        for _ in range(length - 1):
            if random.random() < 0.3:
                name += random.choice(confusing)
            else:
                name += random.choice(chars + string.digits)
        
        return name
    
    def minify(self, code):
        """Minifikasi kode Lua"""
        lines = code.split('\n')
        minified = []
        
        in_multiline_comment = False
        in_multiline_string = False
        
        for line in lines:
            # Handle multi-line comments
            if '--[[' in line:
                in_multiline_comment = True
            if in_multiline_comment:
                if ']]' in line:
                    in_multiline_comment = False
                continue
            
            # Remove single-line comments
            if '--' in line and not in_multiline_string:
                comment_pos = line.find('--')
                # Check if -- is inside a string
                before_comment = line[:comment_pos]
                single_quotes = before_comment.count("'")
                double_quotes = before_comment.count('"')
                
                # If not inside string, remove comment
                if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                    line = line[:comment_pos]
            
            # Remove leading/trailing whitespace
            line = line.strip()
            
            if line:
                minified.append(line)
        
        return '\n'.join(minified)
    
    def encode_string_simple(self, s):
        """Encode string dengan cara yang kompatibel dengan semua Lua"""
        # Gunakan byte array yang dijamin work
        byte_array = [str(ord(c)) for c in s]
        return f"(string.char({','.join(byte_array)}))"
    
    def encode_string_base64(self, s):
        """Encode string dengan base64 + custom decode"""
        encoded = base64.b64encode(s.encode()).decode()
        
        # Custom base64 decoder yang pure Lua
        decoder = f"""(function()
    local b64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    local data = '{encoded}'
    local result = {{}}
    
    for i = 1, #data, 4 do
        local a, b, c, d = data:byte(i, i+3)
        if not a then break end
        
        local n = (b64chars:find(string.char(a)) - 1) * 262144
        n = n + (b and (b64chars:find(string.char(b)) - 1) * 4096 or 0)
        n = n + (c and (b64chars:find(string.char(c)) - 1) * 64 or 0)
        n = n + (d and (b64chars:find(string.char(d)) - 1) or 0)
        
        table.insert(result, string.char(math.floor(n / 65536)))
        if b then table.insert(result, string.char(math.floor(n / 256) % 256)) end
        if c then table.insert(result, string.char(n % 256)) end
    end
    
    return table.concat(result)
end)()"""
        return decoder
