// Small Windows GUI launcher. Keeps source runs pinnable without packaging Python.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Text;
using System.Threading;
using System.Windows.Forms;

[assembly: AssemblyTitle("Repository Builder")]
[assembly: AssemblyProduct("Engineering Playbook Repository Builder")]
[assembly: AssemblyDescription("Create repositories with the Engineering Playbook")]

internal static class Launcher
{
    internal const string AppId = "EngineeringPlaybook.RepositoryBuilder";
    private static string Executable { get { return Assembly.GetExecutingAssembly().Location; } }

    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            if (args.Length == 2 && args[0] == "--shortcut")
            {
                Native.CreateShortcut(Path.GetFullPath(args[1]), Executable);
                return 0;
            }
            string directory = Path.GetDirectoryName(Executable);
            string bundled = Path.Combine(directory, "_runtime", "RepositoryBuilder.Runtime.exe");
            bool packaged = File.Exists(bundled);
            string root = packaged ? directory : Directory.GetParent(directory).FullName;
            string program = packaged ? bundled : Path.Combine(root, ".venv", "Scripts", "python.exe");
            if (!File.Exists(program))
                throw new FileNotFoundException("The app runtime is missing. Reinstall the app, or set up .venv for a source checkout.", program);
            string arguments = packaged ? "" : "-m repository_builder";
            if (args.Length == 2 && (args[0] == "--self-test" || args[0] == "--smoke-test"))
                arguments += " " + args[0] + " \"" + Path.GetFullPath(args[1]).TrimEnd('\\') + "\"";
            Native.SetCurrentProcessExplicitAppUserModelID(AppId);
            string logs = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "EngineeringPlaybook", "RepositoryBuilder", "Logs");
            Directory.CreateDirectory(logs);
            string log = Path.Combine(logs, "launch-" + DateTime.Now.ToString("yyyyMMdd-HHmmss") + "-" + Process.GetCurrentProcess().Id + ".log");
            using (StreamWriter output = new StreamWriter(log, false, Encoding.UTF8))
            using (Process process = new Process())
            {
                output.AutoFlush = true;
                process.StartInfo = new ProcessStartInfo(program, arguments) {
                    WorkingDirectory = root, UseShellExecute = false, CreateNoWindow = true,
                    RedirectStandardOutput = true, RedirectStandardError = true
                };
                process.StartInfo.EnvironmentVariables["FLET_APP_USER_MODEL_ID"] = AppId;
                process.StartInfo.EnvironmentVariables["FLET_APP_RELAUNCH_COMMAND"] = "\"" + Executable + "\"";
                process.StartInfo.EnvironmentVariables["FLET_APP_RELAUNCH_DISPLAY_NAME"] = "Repository Builder";
                process.StartInfo.EnvironmentVariables["FLET_APP_RELAUNCH_ICON"] = Executable + ",0";
                process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs e) {
                    if (e.Data != null) lock (output) output.WriteLine(e.Data);
                };
                process.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs e) {
                    if (e.Data != null) lock (output) output.WriteLine(e.Data);
                };
                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                bool identified = false;
                while (!process.WaitForExit(250))
                {
                    if (identified) continue;
                    foreach (int pid in Native.Descendants(process.Id))
                    {
                        try
                        {
                            using (Process child = Process.GetProcessById(pid))
                            {
                                IntPtr window = child.MainWindowHandle;
                                if (window == IntPtr.Zero || !child.MainWindowTitle.StartsWith("Repository Builder")) continue;
                                // Older Flet clients do not read FLET_APP_RELAUNCH_* yet.
                                // Stamp only this launcher's own descendant window.
                                Native.SetWindowIdentity(window, Executable);
                                identified = true;
                                lock (output) output.WriteLine("Windows taskbar identity configured for Repository Builder.");
                                break;
                            }
                        }
                        catch (ArgumentException) { } // Child already exited.
                        catch (InvalidOperationException) { }
                        catch (COMException e) { lock (output) output.WriteLine(e.Message); }
                    }
                }
                process.WaitForExit(); // Drain asynchronous output callbacks.
                if (process.ExitCode != 0)
                    throw new InvalidOperationException("Repository Builder could not start. See " + log);
            }
            return 0;
        }
        catch (Exception e)
        {
            if (args.Length == 0)
                MessageBox.Show(e.Message, "Repository Builder", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}

internal static class Native
{
    [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
    internal static extern int SetCurrentProcessExplicitAppUserModelID(string appId);
    [DllImport("shell32.dll")]
    private static extern int SHGetPropertyStoreForWindow(IntPtr hwnd, ref Guid iid, out IPropertyStore store);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr CreateToolhelp32Snapshot(uint flags, uint pid);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern bool Process32FirstW(IntPtr snapshot, ref ProcessEntry entry);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern bool Process32NextW(IntPtr snapshot, ref ProcessEntry entry);
    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr handle);

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct ProcessEntry
    {
        public uint size, usage, pid;
        public UIntPtr heap;
        public uint module, threads, parentPid;
        public int priority;
        public uint flags;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 260)] public string filename;
    }

    internal static HashSet<int> Descendants(int root)
    {
        HashSet<int> found = new HashSet<int> { root };
        Dictionary<int, int> parents = new Dictionary<int, int>();
        IntPtr snapshot = CreateToolhelp32Snapshot(2, 0);
        if (snapshot == new IntPtr(-1)) return found;
        try
        {
            ProcessEntry entry = new ProcessEntry { size = (uint)Marshal.SizeOf(typeof(ProcessEntry)) };
            if (Process32FirstW(snapshot, ref entry))
                do { parents[(int)entry.pid] = (int)entry.parentPid; } while (Process32NextW(snapshot, ref entry));
            bool changed;
            do {
                changed = false;
                foreach (var pair in parents)
                    if (found.Contains(pair.Value) && found.Add(pair.Key)) changed = true;
            } while (changed);
            return found;
        }
        finally { CloseHandle(snapshot); }
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PropertyKey
    {
        public Guid format;
        public uint id;
        public PropertyKey(uint id) { format = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"); this.id = id; }
    }
    [StructLayout(LayoutKind.Explicit, Size = 24)]
    private struct PropVariant
    {
        [FieldOffset(0)] public ushort type;
        [FieldOffset(8)] public IntPtr value;
    }
    [ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IPropertyStore
    {
        void GetCount(out uint count);
        void GetAt(uint index, out PropertyKey key);
        void GetValue(ref PropertyKey key, out PropVariant value);
        void SetValue(ref PropertyKey key, ref PropVariant value);
        void Commit();
    }

    private static void Set(IPropertyStore store, uint id, string text)
    {
        PropertyKey key = new PropertyKey(id);
        PropVariant value = new PropVariant { type = 31, value = Marshal.StringToCoTaskMemUni(text) };
        try { store.SetValue(ref key, ref value); }
        finally { Marshal.FreeCoTaskMem(value.value); }
    }

    internal static void SetWindowIdentity(IntPtr window, string executable)
    {
        Guid iid = typeof(IPropertyStore).GUID;
        IPropertyStore store;
        Marshal.ThrowExceptionForHR(SHGetPropertyStoreForWindow(window, ref iid, out store));
        try
        {
            Set(store, 2, "\"" + executable + "\"");
            Set(store, 3, executable + ",0");
            Set(store, 4, "Repository Builder");
            Set(store, 5, Launcher.AppId);
            store.Commit();
        }
        finally { Marshal.ReleaseComObject(store); }
    }

    [ComImport, Guid("00021401-0000-0000-C000-000000000046")]
    private class ShellLink { }
    [ComImport, Guid("000214F9-0000-0000-C000-000000000046"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IShellLink
    {
        void GetPath(IntPtr file, int max, IntPtr data, uint flags);
        void GetIDList(out IntPtr list);
        void SetIDList(IntPtr list);
        void GetDescription(IntPtr text, int max);
        void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string text);
        void GetWorkingDirectory(IntPtr directory, int max);
        void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string directory);
        void GetArguments(IntPtr args, int max);
        void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string args);
        void GetHotkey(out short key);
        void SetHotkey(short key);
        void GetShowCmd(out int show);
        void SetShowCmd(int show);
        void GetIconLocation(IntPtr icon, int max, out int index);
        void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string icon, int index);
        void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string path, uint reserved);
        void Resolve(IntPtr hwnd, uint flags);
        void SetPath([MarshalAs(UnmanagedType.LPWStr)] string path);
    }

    internal static void CreateShortcut(string destination, string executable)
    {
        object instance = new ShellLink();
        try
        {
            IShellLink link = (IShellLink)instance;
            link.SetPath(executable);
            string directory = Path.GetDirectoryName(executable);
            link.SetWorkingDirectory(File.Exists(Path.Combine(directory, "_runtime", "RepositoryBuilder.Runtime.exe"))
                ? directory : Directory.GetParent(directory).FullName);
            link.SetDescription("Create a repository with the Engineering Playbook");
            link.SetIconLocation(executable, 0);
            link.SetShowCmd(1);
            IPropertyStore properties = (IPropertyStore)instance;
            Set(properties, 5, Launcher.AppId);
            properties.Commit();
            ((IPersistFile)instance).Save(destination, true);
        }
        finally { Marshal.ReleaseComObject(instance); }
    }
}
