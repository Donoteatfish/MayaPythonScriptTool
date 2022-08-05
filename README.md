# MayaPythonScriptTool
Python script for Maya

## XYPolyTool
用于高低模烘焙前的准备工作
* 自动平滑非UV边界的边，针对柱体展开的UV进行了优化
* 自带部分纠错功能
* 快速重命名，添加后缀
* 记录低模，将名称复制给想要匹配的高模，并修改后缀
* 显示隐藏高低模，滑动检查高低模的匹配
* 快速选择高低模

使用方法：将highlowPolyEditTool.py文件放到Maya的scripts文件夹下，启动Maya使用以下命令在脚本编辑器中导入并显示脚本的UI，也可以将这段代码放到工具架上，方便下次使用
```python
import highlowPolyEditTool;MatchTool = highlowPolyEditTool.highlowPolyEdit();MatchTool.highlowPolyEditUI()
```
