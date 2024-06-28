import subprocess

def get_current_values():
    # Run the vcgencmd command and capture the output
    result = subprocess.run(['vcgencmd', 'pmic_read_adc'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    
    # Dictionary to hold current values
    currents = {}
    
    # Parse the output to extract current values
    for line in output.split('\n'):
        if 'current' in line:
            parts = line.split('=')
            if len(parts) == 2:
                label = parts[0].strip()
                value = float(parts[1].replace('A', '').strip())
                currents[label] = value
    
    return currents

def calculate_total_current(currents):
    total_current = sum(currents.values())
    return total_current

def main():
    currents = get_current_values()
    total_current = calculate_total_current(currents)
    print(f"Total Current: {total_current:.6f} A")

if __name__ == "__main__":
    main()
