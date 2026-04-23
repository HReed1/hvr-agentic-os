package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"regexp"
	"strings"
)

func main() {
	target := flag.String("target", "", "Target command to wrap")
	flag.Parse()

	if *target == "" {
		fmt.Fprintf(os.Stderr, "FATAL: --target required\n")
		os.Exit(1)
	}

	// Native Go regex is RE2: linear time, O(N), inherently immune to ReDoS.
	// This makes it structurally superior to Python's backtracking engine for DLP proxies.
	genomicPattern := regexp.MustCompile(`(?i)[ATCG]{20,}`)
	// VCF coordinates natively take three forms in string/file STDOUT buffers:
	// 1. UCSC string format (e.g. chr1:1000-2000)
	// 2. Exact Tab-Delimited VCF rows (e.g. 1 \t 1234 \t)
	// 3. b37 string regions (e.g. 1:10000).
	// To avoid brittle boundary edge cases against strings like AWS ARNs or timestamps:
	// We utilize DOMAIN-SPECIFIC KNOWLEDGE: Human chromosomes max out at ~249 million positions (9 digits).
	// By enforcing a maximum numerical bound `\d{1,9}`, we mathematically exclude AWS Account IDs (12 digits)
	// while reverting to standard `\b` word bounds, structurally rejecting almost all metadata edge cases perfectly natively.
	vcfPattern := regexp.MustCompile(`(?i)\bchr(?:[1-9]|1[0-9]|2[0-2]|X|Y|M):\d{1,9}(?:-\d{1,9})?\b|^(?:chr)?(?:[1-9]|1[0-9]|2[0-2]|X|Y|M)\t\d{1,9}\t|(?:^|[\s,;])(?:[1-9]|1[0-9]|2[0-2]|X|Y|M):\d{4,9}(?:-\d{1,9})?\b`)

	uuidPattern := regexp.MustCompile(`(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`)

	args := strings.Split(*target, " ")
	cmd := exec.Command(args[0], args[1:]...)

	stdin, err := cmd.StdinPipe()
	if err != nil {
		fmt.Fprintf(os.Stderr, "FATAL: STDIN pipe failure: %v\n", err)
		os.Exit(1)
	}

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Fprintf(os.Stderr, "FATAL: STDOUT pipe failure: %v\n", err)
		os.Exit(1)
	}

	// Transparently expose stderr for debugging tracebacks
	cmd.Stderr = os.Stderr

	err = cmd.Start()
	if err != nil {
		fmt.Fprintf(os.Stderr, "FATAL: failed to start target: %v\n", err)
		os.Exit(1)
	}

	// Goroutine: Stdin pass-through (Host -> Protocol -> Python MCP)
	go func() {
		io.Copy(stdin, os.Stdin)
		stdin.Close()
	}()

	// Main pipeline mapping: Stdout interception (Python MCP -> Protocol -> Host)
	scanner := bufio.NewScanner(stdout)

	// MCP payload limit bursts can be very large; scale scanner buffer to 10MB to prevent arbitrary splits
	buf := make([]byte, 1024*1024)
	scanner.Buffer(buf, 10*1024*1024)

	for scanner.Scan() {
		line := scanner.Text()

		// Active Auditing Matrix - REDACT instead of KILL
		if genomicPattern.MatchString(line) {
			line = genomicPattern.ReplaceAllString(line, "<REDACTED_PHI>")
		}
		if vcfPattern.MatchString(line) {
			line = vcfPattern.ReplaceAllString(line, "<REDACTED_PHI>")
		}
		if uuidPattern.MatchString(line) {
			line = uuidPattern.ReplaceAllString(line, "<REDACTED_PHI>")
		}

		// Validated Clean Payload. Output back to ADK Host layer.
		fmt.Println(line)
	}

	cmd.Wait()
}
