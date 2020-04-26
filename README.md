# Computer-Networks-CSE-5344-Project-3-Simulation-of-TCP
Simulation of TCP protocol and creating communication protocol for three host systems.

The main idea of this project is to simulate the TCP protocol, which is transport layer protocol. It had to be done in an interesting way in that a communication protocol had to be created for three host systems, that were connected via different links. The newly built communication protocol is supposed to be similar to TCP and also simulate how TCP works. Please read 'Project 3.pdf' for more details.

This project was developed in a Unix environment and written in Python 3.5. Therefore, all testing routines conducted cover the functionality of the project only in a Unix environment.

Instructions for Execution:
1. Open 4 terminal windows.
2. Change the directory in all four terminal windows to where the python scripts for the project are.
3. First off, run the 'routers.py' script by typing 'python3 routers.py' in one terminal.
4. Run 'ann.py,' 'jan.py,' and 'chan.py,' in the remaining terminal windows by typing 'python3 ann.py,' 'python3 jan.py,' and 'python3 chan.py.'
5. After execution is finished, check the log files in 'Supplemental Text Files' to check results. For example, communication between Ann and Jan could be observed in 'AnnJanLog.txt' in Ann's perspective. Additionally, each packet's trace through the routers can be observed in the terminal window that ran 'router.py.'

Assumptions Made:
1.Requirements on retransmission on packet loss was not clear. Consequently, that is not implemented.
2. After the routers are kicked off, it is assumed that they will always be running, since there is no requirement that specifies the termination of them.
3. It was assumed that Jan talks to Ann, Ann talks to Chan, and Chan talks to Jan.
4. Scripts have to be run in the order 'jan.py,' 'chan.py,' and 'ann.py.'
5. The costs of communication among routers never change.
6. Mission 3 starts right after Chan gets terminated.
