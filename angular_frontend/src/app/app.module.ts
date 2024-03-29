import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http'
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Angular Material imports
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './app.component';
import { IssueComponent } from './issue/issue.component';
import { IssueListComponent } from './issue-list/issue-list.component';
import { CommentComponent } from './comment/comment.component';
import { CommentListComponent } from './comment-list/comment-list.component';
import { CreateIssueComponent } from './create-issue/create-issue.component';
import { EditIssueComponent } from './edit-issue/edit-issue.component';
import { CreateCommentComponent } from './create-comment/create-comment.component';
import { SingleIssueComponent } from './single-issue/single-issue.component';
import { HeaderComponent } from './header/header.component';

import { IssueService } from './model/rest-services/issue.service';
import { IssueCacheService } from './model/services/issue-cache.service';
import { ErrorDialogueComponent } from './error-dialogue/error-dialogue.component';

@NgModule({
	declarations: [
		AppComponent,
		IssueComponent,
		IssueListComponent,
		CommentComponent,
		CommentListComponent,
		CreateIssueComponent,
		EditIssueComponent,
		CreateCommentComponent,
		SingleIssueComponent,
		HeaderComponent,
		ErrorDialogueComponent
	],
	imports: [
		BrowserModule,
		AppRoutingModule,
		HttpClientModule,
		FormsModule,
		ReactiveFormsModule,

		// Angular Material modules
		MatCardModule,
		MatFormFieldModule,
		MatInputModule,
		MatButtonModule,
		MatCheckboxModule,
		MatSnackBarModule,
		MatSelectModule,
		MatToolbarModule,
		MatListModule,
		MatDividerModule,
		MatProgressSpinnerModule,
		MatDialogModule,
		BrowserAnimationsModule
	],
	providers: [
		IssueService,
		IssueCacheService
	],
	entryComponents: [ErrorDialogueComponent],
	bootstrap: [AppComponent]
})
export class AppModule { }
