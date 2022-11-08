"""
    shell 交互生成文件

    测试 python shell.py xxx
"""
import sys
import argparse
from palp.tool.create_spider import CreateSpider
from palp.tool.create_project import CreateProject


def generator():
    if len(sys.argv) == 1:
        sys.argv.append('--h')  # 无参数默认输出帮助

    parser = argparse.ArgumentParser(description="Palp 创建爬虫模板")
    parser.add_argument('-p', '--project', help='创建爬虫项目如：palp create -p <project_name>')
    parser.add_argument('-s', '--spider', nargs='+', help='创建爬虫如：palp create -s <spider_name> <spider_type>')
    args = parser.parse_args()

    # 创建 spider
    if args.spider:
        args_spider = args.spider
        if len(args_spider) == 1:
            spider_name = args_spider[0]
            spider_type = 1
        else:
            spider_name = args_spider[0]
            spider_type = int(args_spider[1])

        if spider_type not in [1, 2]:
            raise ValueError('spider 只能是 1 或 2 ！')
        CreateSpider(spider_name, spider_type).create()

    # 创建项目
    if args.project:
        project_name = args.project
        CreateProject(project_name).create()


def helper():
    print("palp 操作命令如下")
    print("\tpalp create [options] [args]")
    print("\n可选 options:")
    cmds = {"-p": "即 project，创建爬虫项目", "-s": "即 spider，创建爬虫"}
    for cmdname, cmdclass in sorted(cmds.items()):
        print("\t%s\t\t%s" % (cmdname, cmdclass))

    print("\n可选 args:")
    cmds = {"1": "创建 spider 时，创建普通 spider", "2": "创建 spider 时，创建分布式 spider"}
    for cmdname, cmdclass in sorted(cmds.items()):
        print("\t%s\t\t%s" % (cmdname, cmdclass))

    print("\n示例:")
    print("\tpalp create -p demo")
    print("\tpalp create -s baidu 1")


def main():
    args = sys.argv
    if len(args) < 2:
        helper()
        return

    command = args.pop(1)
    if command == "create":
        generator()
    else:
        helper()


if __name__ == '__main__':
    helper()
