import os
from helpers.console import write_to_console, print_deeplinks, BColors
from helpers.app_links import check_dals
import helpers.setup
import helpers.adb
import helpers.get_schemes
import helpers.poc

APKTOOL_PATH = 'apktool'
ADB_PATH = 'adb'
DEFAULT_STRINGS_FILE = '/res/values/strings.xml'
DEFAULT_MANIFEST_FILE = '/AndroidManifest.xml'
POC_FILENAME = 'poc.html'
POC_DEST_DIR = '/sdcard/'

def main(strings_file, manifest_file, package, apk, op, verbose, cicd):
    deeplinks = helpers.get_schemes.get_schemes(strings_file, manifest_file)

    if op in [helpers.setup.OP_LIST_ALL, helpers.setup.OP_LIST_APPLINKS]:
        only_applinks = op == helpers.setup.OP_LIST_APPLINKS
        print_deeplinks(deeplinks, only_applinks)

    if op == helpers.setup.OP_VERIFY_APPLINKS:
        check_dals(deeplinks, apk, package, verbose, cicd)

    if op in [helpers.setup.OP_BUILD_POC, helpers.setup.OP_LAUNCH_POC]:
        helpers.poc.write_deeplinks_to_file(deeplinks, POC_FILENAME)
        write_to_console(
            f'Finished writing POC to local file {POC_FILENAME}',
            BColors.OKGREEN
        )

    if op == helpers.setup.OP_LAUNCH_POC:
        helpers.adb.check_device_requirements(package, apk, ADB_PATH)
        helpers.adb.write_file_to_device(POC_FILENAME, POC_DEST_DIR)
        helpers.adb.open_file_in_device_with_chrome(POC_DEST_DIR + POC_FILENAME)

    if op == helpers.setup.OP_TEST_WITH_ADB:
        helpers.adb.check_device_requirements(package, apk, ADB_PATH)
        for activity, handlers in deeplinks.items():
            write_to_console(f'\nActivity: {activity}\n', BColors.BOLD)
            for deeplink in handlers:
                if deeplink.startswith('http'):
                    write_to_console(f'\nTesting deeplink: {deeplink}', BColors.OKGREEN)
                    os.system(
                        f'adb shell am start -a android.intent.action.VIEW -d "{deeplink}"'
                    )
                    input("Press 'Enter' to test next App Link ...")

if __name__ == '__main__':
    args = helpers.setup.get_parsed_args()
    if args.apk is not None:
        helpers.setup.decompile_apk(args.apk)
        apk_filename = os.path.basename(args.apk).split('.apk')[0]
        strings_file_path = open(apk_filename + DEFAULT_STRINGS_FILE,
                                 encoding='utf-8')
        manifest_file_path = open(apk_filename + DEFAULT_MANIFEST_FILE,
                                  encoding='utf-8')
        main(strings_file=strings_file_path,
            manifest_file=manifest_file_path,
            package=args.package,
            apk=args.apk,
            op=args.op,
            verbose=args.verbose or args.cicd,
            cicd=args.cicd)
        if args.clear or args.cicd:
            print('Clearing decompiled directory')
            os.system(f'rm -rf {dir}')
    else:
        strings_file_path = open(args.strings, encoding='utf-8')
        manifest_file_path = open(args.manifest, encoding='utf-8')
        main(strings_file=strings_file_path,
             manifest_file=manifest_file_path,
             package=args.package,
             apk=args.apk,
             op=args.op,
             verbose=args.verbose or args.cicd,
             cicd=args.cicd)
