import { Component, OnInit, ViewChild } from "@angular/core";
import { MatDialog } from "@angular/material/dialog";
import { Subject, timer } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
	selector: "app-root",
	templateUrl: "./app.component.html",
	styleUrls: ["./app.component.scss"],
})
export class AppComponent implements OnInit {
	title = "codenames-app";
	@ViewChild("#iFrame") myFrame!: HTMLElement;
	pulse = false;
	showDummy = true;
	loaded = new Subject();

	constructor(private _dialog: MatDialog) {}

	ngOnInit(): void {
		timer(2000, 1000)
			.pipe(takeUntil(this.loaded))
			.subscribe(() => {
				console.log("Doing");
				this.pulse = true;
				setTimeout(() => {
					this.pulse = false;
				});
			});
	}

	loadedSuccessfully() {
		this.loaded.next();
		this.showDummy = false;
	}
}
