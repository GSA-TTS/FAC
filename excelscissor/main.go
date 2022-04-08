package main

import (
	"flag"
	"fmt"
	"log"
	"strings"

	"github.com/fatih/color"
	"github.com/xuri/excelize/v2"
)

func main() {
	filenamePtr := flag.String("filename", "9165120211.xlsx", "An Excel file")
	flag.Parse()
	if !strings.Contains(*filenamePtr, "xlsx") {
		log.Fatalf("[%s] must be an XLSX spreadsheet.", *filenamePtr)
	}
	xls, err := excelize.OpenFile(*filenamePtr)
	if err != nil {
		log.Fatal("could not open Excel file")
	}

	log.Printf("Number of sheets: %d\n", len(xls.GetSheetList()))

	color.Magenta("Let's look at column D")
	fmt.Println("")
	for ndx := 1; ndx < 50; ndx++ {
		ref := fmt.Sprintf("D%d", ndx)
		contents, err := xls.GetCellValue("General Info", ref)
		if err != nil {
			log.Printf("[%s] could not reference cell\n", ref)
		} else {
			fmt.Printf("[%s] %s\n", ref, contents)
		}
	}

	color.Magenta("Who submitted this?")
	who, err := xls.GetCellValue("General Info", "D25")
	if err == nil {
		fmt.Println(who)
	}
}
