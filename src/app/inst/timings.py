import time

# Function to get current time with milliseconds precision
def get_current_time():
    return time.strftime("%H:%M:%S") + '.' + str(int(time.time() * 1000) % 1000).zfill(3)

# Main function to continuously display the current time
def main():
    try:
        while True:
            current_time = get_current_time()
            print(current_time, end='\r')  # Print on the same line
            time.sleep(0.001)  # Sleep for 1 millisecond
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
