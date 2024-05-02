"""
COMPSCI 424 Program 3
Name: Noah Anderson
"""

import sys
import threading  # standard Python threading library
import random

# (Comments are just suggestions. Feel free to modify or delete them.)

# When you start a thread with a call to "threading.Thread", you will
# need to pass in the name of the function whose code should run in
# that thread.

# If you want your variables and data structures for the banker's
# algorithm to have global scope, declare them here. This may make
# the rest of your program easier to write. 
#  
# Most software engineers say global variables are a Bad Idea (and 
# they're usually correct!), but systems programmers do it all the
# time, so I'm allowing it here.
maximum = []
available = []
allocation = []
total = []
need = []
request = []
num_processes, num_resources = 0, 0


# Let's write a main method at the top
def main():
    global maximum, available, allocation, total, need, request, num_processes, num_resources
    # Code to test command-line argument processing.
    # You can keep, modify, or remove this. It's not required.
    if len(sys.argv) < 3:
        sys.stderr.write("Not enough command-line arguments provided, exiting.")
        sys.exit(1)

    print("Selected mode:", sys.argv[1])
    print("Setup file location:", sys.argv[2])
    # 1. Open the setup file using the path in argv[2]

    with open(sys.argv[2], 'r') as setup_file:
        # 2. Get the number of resources and processes from the setup
        # file, and use this info to create the Banker's Algorithm
        # data structures
        num_resources = int(setup_file.readline().split()[0])
        num_processes = int(setup_file.readline().split()[0])
        setup_file.readline()
        request = [[0] * num_resources for _ in range(num_processes)]
        # 3. Use the rest of the setup file to initialize the data structures
        # (you fill in this part)
        available = [int(x) for x in (setup_file.readline().split())]
        print(available, "available")

        setup_file.readline()
        i = 0
        while i < num_processes:
            maxlist = [int(x) for x in (setup_file.readline().split())]
            maximum.append(maxlist)
            i += 1
        print(maximum, "maximum")
        setup_file.readline()
        i = 0
        while i < num_processes:
            allolist = [int(x) for x in (setup_file.readline().split())]
            allocation.append(allolist)
            i += 1
        print(allocation, "allocation")

        i = 0
        for x in range(num_resources):
            total.append(0)
            total[i] += available[i]
            for y in allocation:
                total[i] += y[i]
            i += 1

        i = 0
        j = 0
        while i < num_processes:
            need.append([0]*num_resources)
            while j < num_resources:
                need[i][j] = maximum[i][j] - allocation[i][j]

                j += 1
            j = 0
            i += 1

        # all setup from file complete, closing file
        setup_file.close()

    # 4. Check initial conditions to ensure that the system is
    # beginning in a safe state: see "Check initial conditions"
    # in the Program 3 instructions
    p = 0
    r = 0

    while p < num_processes:
        while r < num_resources:
            if allocation[p][r] > maximum[p][r]:
                sys.stderr.write("Item in allocation array is larger than corresponding item in"
                                 " maximum array, stopping program.")
                sys.exit(1)
            r += 1
        p += 1

    if sys.argv[1] == "auto":
        handle_threading()
    elif sys.argv[1] == "manual":
        manual()
    # 5. Go into either manual or automatic mode, depending on
    # the value of args[0]; you could implement these two modes
    # as separate methods within this class, as separate classes
    # with their own main methods, or as additional code within
    # this main method.

# fill in other methods here as desired


# code for manual mode
def manual():
    print("\n\nCommand List: \nrequest I of J for K\nrelease I of J for K\nview\nend\n")
    userinput = input("Enter command: ")

    # loop for user menu
    while userinput != "end":
        try:
            if userinput == "view":
                print("\n\n")
                print(maximum, "maximum")
                print(available, "available")
                print(allocation, "allocation")
                print(request, "request")
                print("\n\n")

                userinput = input("Enter command: ")
                continue
            inputlist = userinput.split()
            i = int(inputlist[1])
            j = int(inputlist[3])
            k = int(inputlist[5])
            request[k][j] = i
            if inputlist[0].lower() == "request":
                handle_request(k, j)
            elif inputlist[0].lower() == "release":
                handle_release(k, j)
            else:
                print("Command not recognized, try again")
            userinput = input("Enter command: ")
        except IndexError:
            print("Command not recognized, try again")
            userinput = input("Enter command: ")
        except ValueError:
            print("I, J, and K need to be integer values")
            userinput = input("Enter command: ")

    print("Terminating program...")


# code for auto mode
# randomly generates valid requests, function is called by handle_threads()
def auto():
    random_processes = []
    random_resources = []
    random_requests = []
    for x in range(3):
        random_resources.append(random.randint(0, num_resources-1))
    for x in range(3):
        random_processes.append(random.randint(0, num_processes-1))
    for x in range(3):
        random_requests.append(random.randint(0, num_resources-1))

    random_release_processes = []
    random_release_resources = []
    random_release_requests = []
    for x in random_resources:
        random_release_resources.append(random.randint(0, x))
    for x in random_processes:
        random_release_processes.append(random.randint(0, x))
    for x in random_requests:
        random_release_requests.append(random.randint(0, x))

    i = 0
    while i < 3:
        request[random_processes[i]][random_resources[i]] = random_requests[i]
        handle_request(random_processes[i], random_resources[i])
        handle_release(random_processes[i], random_resources[i])
        i += 1
    print("\n\n")
    print(maximum, "maximum")
    print(available, "available")
    print(allocation, "allocation")
    print(request, "request")
    print("\n\n")


# function to handle requesting resources, and allocates them if safe
def handle_request(i, j):
    global maximum, available, allocation, total, need, request, num_processes, num_resources
    if request[i][j] > need[i][j]:
        print("Process " + str(i) + " requests " + str(request[i][j]) + " units of resource " + str(j))
        sys.stderr.write("The process has exceeded its maximum claim, request aborted\n")
        return
    if request[i][j] > available[j]:
        print("Process " + str(i) + " requests " + str(request[i][j]) + " units of resource " + str(j))
        sys.stderr.write("Process must wait, resources are not available.\n")
        return
    temp_available = available.copy()
    temp_allocation = allocation.copy()
    temp_need = need.copy()

    available[j] -= request[i][j]

    allocation[i][j] += request[i][j]

    need[i][j] -= request[i][j]

    if check_safety():
        print("Process " + str(i) + " requests " + str(request[i][j]) + " units of resource " + str(j) + ": Successful")
        return
    else:
        available = temp_available.copy()
        allocation = temp_allocation.copy()
        need = temp_need.copy()
        print("Process " + str(i) + " requests " + str(request[i][j]) +
              " units of resource " + str(j) + ": Denied - will cause an unsafe state")
        return


# function to handle releasing allocated resources
def handle_release(i, j):
    global maximum, available, allocation, total, need, request, num_processes, num_resources
    if allocation[i][j] < request[i][j]:
        print("Process " + str(i) + " releases " + str(request[i][j]) + " units of resource " + str(j))
        sys.stderr.write("Too many resources requested for release, command aborted.\n")
        return

    available[j] += request[i][j]

    allocation[i][j] -= request[i][j]

    need[i][j] += request[i][j]

    print("Process " + str(i) + " releases " + str(request[i][j]) + " units of resource " + str(j) + ": Successful")
    return


# function to handle creating and joining threads
def handle_threading():
    threads = list()
    for index in range(num_processes):
        x = threading.Thread(target=auto(), args=())
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()


def check_safety():
    global need, allocation, available

    m = len(available)
    n = len(need)

    # Initialize Work and Finish vectors
    work = available.copy()
    finish = [False] * n

    # Step 2
    while True:
        # Find an index i such that Finish[i] == False and Need[i] <= Work
        i = None
        for j in range(n):
            if not finish[j]:
                if all(need[j][k] <= work[k] for k in range(m)):
                    i = j
                    break

        if i is None:
            break  # No such i exists, exit loop

        # Step 3
        work = [work[k] + allocation[i][k] for k in range(m)]
        finish[i] = True

    # Step 4
    if all(finish):
        return True  # System is in a safe state
    else:
        return False  # System is not in a safe state


main()  # call the main function
