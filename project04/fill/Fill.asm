// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

@color    
M=0      

(LOOP)

@SCREEN
D=A
@pixels
M=D         

@KBD    
D=M
@BLACK
D;JGT    
  
@color
M=0       
@COLOR_SCREEN
0;JMP     
  
(BLACK)
@color
M=-1    

(COLOR_SCREEN)
@color
D=M
@pixels
A=M         
M=D        
   
@pixels
M=M+1
D=M
        
@24576
D=D-A
@COLOR_SCREEN
D;JLT

@LOOP
0;JMP // infinite loop