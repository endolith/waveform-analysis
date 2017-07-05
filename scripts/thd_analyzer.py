
# if __name__ == '__main__':
#
#
#    try:
#
#        if files:
#            for filename in files:
#                try:
#                    analyze_channels(filename, THDN)
#                except IOError:
#                    print('Couldn\'t analyze "' + filename + '"\n')
#                print('')
#        else:
#            sys.exit("You must provide at least one file to analyze")
#    except BaseException as e:
#        print('Error:')
#        print(e)
#        raise
#    finally:
#        # Otherwise Windows closes the window too quickly to read
#        input('(Press <Enter> to close)')
#


def thd_analyzer(files):
    import sys

    if files:
        for filename in files:
            try:
                analyze_channels(filename, THDN)
            except IOError:
                print('Couldn\'t analyze "' + filename + '"\n')
            print('')
    else:
        sys.exit("You must provide at least one file to analyze:\n"
                 "python wave_analyzer.py filename.wav")
