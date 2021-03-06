


#include "Swr_Model.h"

using namespace Common;




int main(int argc, char** argv)
{

	printf("*******************************************************************\n");
	if (argc < 2)
	{
		printf("This tool is for extract/repack some files of StarwarsRacer,\n\
 Notice: on Extract, a listFiles.xml will be generated. it's to keep the same order for repack.\n\
 Usage: 'Pack.exe [options] file.bin ...' to extract, 'Pack.exe [options] folder' or 'Pack.exe [options] --out filenameToCreate.bin listFiles1.xml listFiles2.xml ...' to repack\n\
 Files formats supported : bin for model ('model' must be inside the filename).\n\
 Options : '-NoWait', '-AlwaysWait', '-WaitOnError' (default), or '-WaitOnWarning'.\n\
*******************************************************************\n\
Press Enter to continue.\n");
		getchar();
		return 1;
	}
	std::vector<string> arguments = initApplication(argc, argv);

	if (arguments.size() == 0)
	{
		printf("Error not enougth arguments.\n");
		notifyError();
		waitOnEnd();
		return 1;
	}


	//serach for options
	string filenameToCreate = "";
	size_t nbArg = arguments.size();
	for (size_t i = 0; i < nbArg; i++)
	{
		if (arguments.at(i) == "--out")
		{
			arguments.erase(arguments.begin() + i);
			--nbArg;

			if (i < nbArg)
			{
				filenameToCreate = arguments.at(i);

				arguments.erase(arguments.begin() + i);
				--nbArg;
				--i;
			}
		}
	}



	if (arguments.size() == 0)
	{
		printf("Error not enougth arguments.\n");
		notifyError();
		waitOnEnd();
		return 1;
	}



	if (filenameToCreate.length()!=0)										//case "--out filenameToCreate listFiles.xml" or "--out filenameToCreate fileToPack1.bin fileToPack2.bin fileToPack3.bin ..."
	{
		if (toLowerCase(filenameToCreate).find("model") != std::string::npos)				//it's a model
		{
			Swr_Model* model = new Swr_Model();
			model->unsplitModelFile_ListFilesXml(filenameToCreate, arguments, true);
			delete model;
		}
		printf("finished.\n");
		waitOnEnd();
		return 0;
	}


	nbArg = arguments.size();
	for (size_t i = 0; i < nbArg; i++)
	{
		string filename = arguments.at(i);
		string extension = extensionFromFilename(filename, true);
		string basefilename = filename.substr(0, filename.length() - (extension.size() + 1)) ;
		string name = Common::nameFromFilename(basefilename);

		printf("Process on %s. Please Wait...\n", filename.c_str());

		if (extension == "bin")											//it's a file to unpack
		{
			if (toLowerCase(name).find("model") != std::string::npos)				//it's a model
			{
				Swr_Model* model = new Swr_Model();
				model->splitModelFile(filename, true);
				delete model;
			}


		}else if (extension == "") {									//it's a folder to pack
			
			if (toLowerCase(name).find("model") != std::string::npos)				//it's a model
			{
				Swr_Model* model = new Swr_Model();
				model->unsplitModelFile(filename, true);
				delete model;
			}
		}else {
			printf("Error on arguments.\n");
			notifyError();
		}
	}

	printf("finished.\n");
	waitOnEnd();
	return 0;
}