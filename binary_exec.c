/*把所有传入的参数原样传到目标python里*/
/*用来跟python35 embbed版本配合做成二进制release*/
#include<stdlib.h>
#include<string.h>
int main(int argc,char *argv[]){
	char exec_cmd[65535];
	strcpy(exec_cmd,"%ComSpec% /k .\\pythonbin\\python.exe .\\script\\shuoshuo.py ");
	int i,pos=strlen(exec_cmd);
	for(i=1;i<argc;i++){
		pos += sprintf(exec_cmd+pos," %s ",argv[i]);
	}
	system(exec_cmd);
}
