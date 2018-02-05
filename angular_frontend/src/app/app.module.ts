import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http'

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
    SingleIssueComponent
  ],
  imports: [
	  BrowserModule,
	  AppRoutingModule,
	  HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
