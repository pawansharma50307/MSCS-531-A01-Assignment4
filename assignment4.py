from m5.objects import *
import m5

# -----------------------------
# System Configuration
# -----------------------------
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# -----------------------------
# CPU Configuration
# -----------------------------
cpu = DerivO3CPU()  # Out-of-order CPU
cpu.numThreads = 2   # Enable SMT (for SMT experiment)
cpu.width = 2        # Superscalar: 2 instructions per cycle

# Pipeline widths
cpu.fetchWidth = cpu.decodeWidth = cpu.renameWidth = cpu.issueWidth = 2
cpu.commitWidth = 2

# Branch Predictor
cpu.branchPred = TournamentBP()
cpu.branchPred.BTBEntries = 512
cpu.branchPred.globalPredictorSize = 4096
cpu.branchPred.localPredictorSize = 1024

# -----------------------------
# Memory Configuration
# -----------------------------
system.membus = SystemXBar()
system.cpu = cpu

system.cpu.icache_port = system.membus.slave
system.cpu.dcache_port = system.membus.slave

system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.master

# -----------------------------
# Workload Setup
# -----------------------------
# Replace with any small test program
binary = 'tests/test-progs/hello/bin/x86/linux/hello'  # Placeholder workload
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# -----------------------------
# Root and Simulation Setup
# -----------------------------
root = Root(full_system = False, system = system)

# Reset and enable statistics
m5.stats.reset()
m5.stats.enable()

print("Starting gem5 simulation...")
exit_event = m5.simulate()
print("Simulation finished at tick %d due to %s" % (m5.curTick(), exit_event.getCause()))

# -----------------------------
# Collect and Print Key Statistics
# -----------------------------
committed_insts = m5.stats.find('system.cpu.committedInsts')
num_cycles = m5.stats.find('system.cpu.numCycles')

ipc = committed_insts.value / num_cycles.value if num_cycles.value != 0 else 0

branch_mispred = m5.stats.find('system.cpu.branchPred.condMiss').value

# Simple textual output
print("\n===== ILP Simulation Results =====")
print(f"Total Cycles: {num_cycles.value}")
print(f"Committed Instructions: {committed_insts.value}")
print(f"Instructions Per Cycle (IPC): {ipc:.3f}")
print(f"Branch Mispredictions: {branch_mispred}")
print("=================================\n")

# Additional simple metrics
fetch_stalls = m5.stats.find('system.cpu.fetch.stalls').value
decode_stalls = m5.stats.find('system.cpu.decode.stalls').value
execute_stalls = m5.stats.find('system.cpu.execute.stalls').value
commit_stalls = m5.stats.find('system.cpu.commit.stalls').value

print("Pipeline Stage Stalls:")
print(f"Fetch Stage Stalls: {fetch_stalls}")
print(f"Decode Stage Stalls: {decode_stalls}")
print(f"Execute Stage Stalls: {execute_stalls}")
print(f"Commit Stage Stalls: {commit_stalls}")
