import { Component, Input, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Title } from '@angular/platform-browser';

import { TranslateService } from '@ngx-translate/core';
import { map } from 'rxjs/operators';

import { UserRepositoryService } from 'app/core/repositories/users/user-repository.service';
import { BaseViewComponent } from 'app/site/base/base-view';
import { ViewBasePoll } from 'app/site/polls/models/view-base-poll';

@Component({
    selector: 'os-poll-progress',
    templateUrl: './poll-progress.component.html',
    styleUrls: ['./poll-progress.component.scss']
})
export class PollProgressComponent extends BaseViewComponent implements OnInit {
    @Input()
    public set poll(value: ViewBasePoll) {
        this._poll = value;
        console.log("set poll");
    }

    public get poll(): ViewBasePoll {
        return this._poll;
    }

    private _poll: ViewBasePoll;


    public votescast: number;
    public max: number;
    public valueInPercent: number;

    public constructor(
        title: Title,
        protected translate: TranslateService,
        snackbar: MatSnackBar,
        private userRepo: UserRepositoryService
    ) {
        super(title, translate, snackbar);
    }

    /**
     * OnInit.
     * Sets the observable for groups.
     */
    public ngOnInit(): void {
        console.log("On init", this.poll);
        if (this.poll) {
            console.log(this.poll, this.poll.votesvalid, this.poll.voted.length);
            const ids = new Set();
            for (const option of this.poll.options) {
                for (const vote of option.votes) {
                    if (vote.user_id) {
                        ids.add(vote.user_id);
                    }
                }
            }
            console.log(ids.size);
            this.votescast = ids.size;
            this.userRepo
                .getViewModelListObservable()
                .pipe(
                    map(users =>
                        users.filter(user => user.is_present && this.poll.groups_id.intersect(user.groups_id).length)
                    )
                )
                .subscribe(users => {
                    this.max = users.length;

                    this.valueInPercent = (this.votescast / this.max) * 100;
                });
        }
    }
}
